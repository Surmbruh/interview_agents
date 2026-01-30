import json
from typing import List, Dict, Any

class LoggerUtils:
    """
    Utility class for logging interview data to a JSON file.
    """
    
    @staticmethod
    def save_log(participant_name: str, turns: List[Dict[str, Any]], final_feedback: str, filename: str = "interview_log.json"):
        """
        Save the interview log to a JSON file with the specified structure.
        
        Args:
            participant_name: Name of the candidate.
            turns: List of turn data dictionaries. Each dict should have 'turn_id', 'internal_thoughts', 'user_input', 'agent_response'.
            final_feedback: The comprehensive report generated at the end.
            filename: The file path to save the log to.
        """
        data = {
            "participant_name": participant_name,
            "turns": turns,
            "final_feedback": final_feedback
        }
        
        try:
            import os
            abs_path = os.path.abspath(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Interview log saved to {abs_path}")
        except Exception as e:
            print(f"Error saving interview log: {e}")
