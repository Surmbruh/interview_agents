"""
Main CLI interface for Multi-Agent Interview Coach.
Provides interactive command-line interview experience.
"""
import uuid
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load env before importing graph
load_dotenv()

from graph import graph
from utils.log_config import setup_logging, get_logger

# Initialize logging
setup_logging(level="INFO")
logger = get_logger("main")


def main():
    print("\n" + "="*50)
    print("    Multi-Agent Interview Coach")
    print("="*50)
    
    # 1. Collect Scenario Info
    try:
        scenario_num = input("\nEnter scenario number (1-5): ").strip()
        scenario_id = int(scenario_num) if scenario_num else 1
    except ValueError:
        scenario_id = 1
        
    # 2. Collect User Info
    print("\nPlease introduce yourself:")
    name = input("Name: ").strip() or "Candidate"
    grade = input("Target Grade (Junior/Middle/Senior): ").strip() or "Middle"
    position = input("Target Position (e.g. Python Backend): ").strip() or "Python Developer"
    
    candidate_info = {
        "Name": name,
        "Position": position,
        "Grade": grade,
        "Experience": "N/A"
    }
    
    # 3. Company Context
    company_profile = """
    Company: TechFin Solutions
    Stack: Python 3.11, Django, FastAPI, PostgreSQL, RabbitMQ, Docker, Kubernetes, AWS.
    Culture: Engineering excellence, clean code, high performance.
    """
    
    # 4. Initialize State
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info("Starting interview Scenario #%d for %s %s", scenario_id, grade, position)
    print(f"\nStarting interview for {grade} {position}...")
    print("Type 'Stop' or 'Стоп' to end the interview.\n")
    
    initial_state = {
        "messages": [],
        "candidate_info": candidate_info,
        "company_profile": company_profile,
        "internal_thoughts": [],
        "interview_log": [],
        "loop_count": 0,
        "topics_covered": [],
        "router_decision": "ANSWER",
        "topic_plan": [],
        "critic_feedback": "",
        "critic_retry_count": 0,
        "current_question": "",
        "current_turn_thoughts": {},
        "session_id": scenario_id
    }
    
    logger.debug("Session started with thread_id: %s", thread_id)
    
    # First invocation (Start signal)
    events = graph.invoke(initial_state, config)
    
    messages = events.get("messages", [])
    if messages:
        last = messages[-1]
        print(f"\nInterviewer: {last.content}")
    
    # Main Loop
    while True:
        try:
            user_input = input("\nYou: ")
        except (KeyboardInterrupt, EOFError):
            user_input = "Stop"
        
        if not user_input:
            continue
        
        logger.debug("User input: %s", user_input[:100])
            
        current_state = {
            "messages": [HumanMessage(content=user_input)]
        }
        
        # Invoke Graph
        events = graph.invoke(current_state, config)
        
        # Check if finished
        new_messages = events.get("messages", [])
        if new_messages:
            last_msg = new_messages[-1]
            if last_msg.content == "INTERVIEW_FINISHED":
                logger.info("Interview completed")
                print("\n[Interview Finished]")
                break
            
            # Print Interviewer response
            print(f"\nInterviewer: {last_msg.content}")
             
    # FINAL SAVING (using session_id)
    report_filename = f"interview_log_{scenario_id}.json"
    
    print("\n" + "="*50)
    print(f"Log saved to: {report_filename}")
    logger.info("Session complete. Log saved to %s", report_filename)


if __name__ == "__main__":
    main()
