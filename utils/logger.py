"""
Utility class for saving interview logs to JSON files.
"""
import json
import os
from typing import List, Dict, Any
from utils.log_config import get_logger

logger = get_logger("logger")


class LoggerUtils:
    """
    Utility class for logging interview data to a JSON file.
    """
    
    @staticmethod
    def save_log(
        participant_name: str, 
        turns: List[Dict[str, Any]], 
        final_feedback: str, 
        filename: str = "interview_log.json"
    ) -> bool:
        """
        Save the interview log to a JSON file with the specified structure.
        
        Args:
            participant_name: Name of the candidate.
            turns: List of turn data dictionaries.
            final_feedback: The comprehensive report generated at the end.
            filename: The file path to save the log to.
            
        Returns:
            True if saved successfully, False otherwise.
        """
        data = {
            "participant_name": participant_name,
            "turns": turns,
            "final_feedback": final_feedback
        }
        
        try:
            abs_path = os.path.abspath(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Interview log saved to %s", abs_path)
            return True
        except Exception as e:
            logger.error("Error saving interview log: %s", e)
            return False
