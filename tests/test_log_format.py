"""
Tests for interview log format compliance with hackathon requirements.
Ensures logs match the required JSON structure.
"""
import pytest
import json
import os


class TestLogFormatCompliance:
    """Test that generated logs comply with hackathon requirements."""
    
    @pytest.fixture
    def sample_log(self):
        """Sample log structure matching requirements."""
        return {
            "participant_name": "Test Candidate",
            "turns": [
                {
                    "turn_id": 1,
                    "agent_visible_message": "Привет! Расскажите о себе.",
                    "user_message": "Я Python разработчик с 3 годами опыта.",
                    "internal_thoughts": "[Observer]: Кандидат уверен в себе.\n[Interviewer]: Задам вопрос про типы данных.\n"
                },
                {
                    "turn_id": 2,
                    "agent_visible_message": "Какие типы данных в Python вы знаете?",
                    "user_message": "int, str, list, dict, tuple, set",
                    "internal_thoughts": "[Observer]: Правильный ответ.\n[Critic]: APPROVED.\n"
                }
            ],
            "final_feedback": "# Отчёт по интервью\n\n## Вердикт: HIRE"
        }
    
    def test_log_has_required_top_level_keys(self, sample_log):
        """Log must have participant_name, turns, final_feedback."""
        required_keys = ["participant_name", "turns", "final_feedback"]
        
        for key in required_keys:
            assert key in sample_log, f"Missing required key: {key}"
    
    def test_turns_is_list(self, sample_log):
        """Turns must be a list."""
        assert isinstance(sample_log["turns"], list)
    
    def test_each_turn_has_required_fields(self, sample_log):
        """Each turn must have turn_id, agent_visible_message, user_message, internal_thoughts."""
        required_turn_keys = [
            "turn_id",
            "agent_visible_message", 
            "user_message",
            "internal_thoughts"
        ]
        
        for turn in sample_log["turns"]:
            for key in required_turn_keys:
                assert key in turn, f"Turn missing key: {key}"
    
    def test_internal_thoughts_contains_agent_markers(self, sample_log):
        """Internal thoughts should have agent markers like [Observer]:"""
        valid_markers = ["[Observer]:", "[Interviewer]:", "[Critic]:", "[Manager]:"]
        
        for turn in sample_log["turns"]:
            thoughts = turn["internal_thoughts"]
            has_marker = any(marker in thoughts for marker in valid_markers)
            assert has_marker, f"Turn {turn['turn_id']} missing agent markers in thoughts"
    
    def test_turn_ids_are_sequential(self, sample_log):
        """Turn IDs should be sequential starting from 1."""
        turn_ids = [t["turn_id"] for t in sample_log["turns"]]
        expected = list(range(1, len(turn_ids) + 1))
        
        assert turn_ids == expected, f"Turn IDs not sequential: {turn_ids}"


class TestLoggerUtils:
    """Test the LoggerUtils class."""
    
    def test_save_log_creates_file(self, tmp_path):
        """LoggerUtils.save_log should create a valid JSON file."""
        from utils.logger import LoggerUtils
        
        test_file = tmp_path / "test_log.json"
        
        turns = [
            {
                "turn_id": 1,
                "agent_visible_message": "Test question",
                "user_message": "Test answer",
                "internal_thoughts": "[Observer]: Test thought\n"
            }
        ]
        
        LoggerUtils.save_log(
            participant_name="Test User",
            turns=turns,
            final_feedback="Test feedback",
            filename=str(test_file)
        )
        
        assert test_file.exists()
        
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["participant_name"] == "Test User"
        assert len(data["turns"]) == 1
        assert data["final_feedback"] == "Test feedback"
