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
    
    # 1. Collect User Info
    print("Please introduce yourself:")
    name = input("Name: ").strip() or "Candidate"
    grade = input("Target Grade (Junior/Middle/Senior): ").strip() or "Middle"
    position = input("Target Position (e.g. Python Backend): ").strip() or "Python Developer"
    
    candidate_info = {
        "Name": name,
        "Position": position,
        "Grade": grade,
        "Experience": "N/A" # Simplified input
    }
    
    # 2. Company Context
    company_profile = """
    Company: TechFin Solutions
    Stack: Python 3.11, Django, FastAPI, PostgreSQL, RabbitMQ, Docker, Kubernetes, AWS.
    Culture: Engineering excellence, clean code, high performance.
    """
    
    # 3. Initialize State
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n🚀 Starting interview for {grade} {position} at TechFin Solutions.")
    print("Type 'Stop' to end the interview.\n")
    
    # Initial State
    # Note: We send a dummy message to trigger the Router/Observer for the first time
    # OR we can manually craft the first question.
    # Architecture decision: Start with router -> Observer -> Interviewer with empty input -> "Start interview" instruction.
    initial_state = {
        "messages": [],
        "candidate_info": candidate_info,
        "company_profile": company_profile,
        "internal_thoughts": [],
        "interview_log": [],
        "loop_count": 0,
        "topics_covered": [],
        "router_decision": "ANSWER", # Default
        "topic_plan": [],
        "critic_feedback": "",
        "critic_retry_count": 0
    }
    
    # Initial trigger
    # The graph expects a message to route.
    # We can fake a "Start" message from System or just run Observer logic manually if message is empty.
    # But router analyzes input. If empty? 
    # Let's handle first turn specially or start with a greeting "Hello".
    
    print("--- Session Started ---")
    
    # First invocation (Start signal)
    # Observer checks updates: if no messages, it generates greeting instruction.
    # Router checks input: if empty -> ANSWER (default) -> Observer (sees no msgs) -> Instruction "Greet"
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
        # Flow: Router(analyze user_input) -> [Observer|Interviewer|Feedback] -> ...
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
             # Should not happen in normal flow
             pass
             
    print("\n-------------------------------------------")
    print(f"📄 Log and Report saved to interview_log.json")

if __name__ == "__main__":
    main()
