import os
import uuid
import sys
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load env before importing graph
load_dotenv()

from graph import graph
from utils.logger import LoggerUtils

def main():
    print("🎓 Welcome to the Multi-Agent Interview Coach!")
    print("-------------------------------------------")
    
    # 1. Collect Scenario Info
    try:
        scenario_num = input("Enter scenario number (1-5): ").strip()
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
    
    print(f"\n🚀 Starting interview Scenario #{scenario_id} for {grade} {position}.")
    print("Type 'Stop' to end the interview.\n")
    
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
    
    print("--- Session Started ---")
    
    # First invocation (Start signal)
    events = graph.invoke(initial_state, config)
    
    messages = events.get("messages", [])
    if messages:
        last = messages[-1]
        print(f"\n👩‍💻 Interviewer: {last.content}")
    
    # Main Loop
    while True:
        try:
            user_input = input("\n👤 You: ")
        except (KeyboardInterrupt, EOFError):
            user_input = "Stop"
        
        if not user_input:
            continue
            
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
                 print("\n🏁 Interview Finished.")
                 break
            
            # Print Interviewer response
            print(f"\n👩‍💻 Interviewer: {last_msg.content}")
        else:
             pass
             
    # FINAL SAVING (using session_id)
    final_state = graph.get_state(config).values
    report_filename = f"interview_log_{scenario_id}.json"
    
    # Extract data for logger
    participant_name = final_state["candidate_info"].get("Name", "Candidate")
    turns = final_state.get("interview_log", [])
    
    # The final feedback is stored in the log file, but we need to generate/extract it
    # Feedback node saves it to interview_log.json by default, let's fix that.
    
    print("\n-------------------------------------------")
    print(f"📄 Log and Report saved to {report_filename}")

if __name__ == "__main__":
    main()
