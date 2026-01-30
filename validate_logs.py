import json
import os
import sys

def validate_log(file_path="interview_log.json"):
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found.")
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            log = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse JSON: {e}")
        return False

    required_keys = ["participant_name", "turns", "final_feedback"]
    for key in required_keys:
        if key not in log:
            print(f"❌ Error: Missing required key '{key}' in log.")
            return False

    print(f"✅ Found log for participant: {log['participant_name']}")
    
    if not isinstance(log["turns"], list):
        print("❌ Error: 'turns' must be a list.")
        return False

    turn_required_keys = ["turn_id", "internal_thoughts", "user_input", "agent_response"]
    for i, turn in enumerate(log["turns"]):
        for key in turn_required_keys:
            if key not in turn:
                print(f"❌ Error: Turn {i+1} (ID: {turn.get('turn_id', 'N/A')}) is missing key '{key}'.")
                return False
        
    print(f"✅ Successfully validated {len(log['turns'])} turns.")
    print("🚀 Log format is correct and complies with project requirements.")
    return True

if __name__ == "__main__":
    success = validate_log()
    sys.exit(0 if success else 1)
