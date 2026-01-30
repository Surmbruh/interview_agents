"""
Pytest configuration and fixtures for Interview Coach tests.
"""
import pytest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables before importing modules
os.environ.setdefault("OPENAI_API_KEY", "test-key-for-unit-tests")
os.environ.setdefault("OPENAI_API_BASE", "https://api.openai.com/v1")


@pytest.fixture
def sample_candidate_info():
    """Sample candidate information for tests."""
    return {
        "Name": "Test Candidate",
        "Position": "Python Backend Developer",
        "Grade": "Middle",
        "Experience": "3 years"
    }


@pytest.fixture
def sample_company_profile():
    """Sample company profile for tests."""
    return """
    Company: TestCorp
    Stack: Python 3.11, Django, PostgreSQL, Docker, Kubernetes
    Culture: Engineering excellence, code review, TDD
    """


@pytest.fixture
def sample_state(sample_candidate_info, sample_company_profile):
    """Sample AgentState for tests."""
    return {
        "messages": [],
        "candidate_info": sample_candidate_info,
        "company_profile": sample_company_profile,
        "internal_thoughts": [],
        "interview_log": [],
        "loop_count": 0,
        "topics_covered": [],
        "router_decision": "ANSWER",
        "topic_plan": ["Python Basics", "Django", "Databases"],
        "critic_feedback": "",
        "critic_retry_count": 0,
        "current_question": "",
        "current_turn_thoughts": {},
        "session_id": 1
    }


@pytest.fixture
def sample_interview_log():
    """Sample interview log matching required format."""
    return {
        "participant_name": "Test Candidate",
        "turns": [
            {
                "turn_id": 1,
                "agent_visible_message": "Привет! Расскажите о себе.",
                "user_message": "Я Python разработчик с 3 годами опыта.",
                "internal_thoughts": "[Observer]: Кандидат уверен.\n[Interviewer]: Спрошу про типы данных.\n"
            }
        ],
        "final_feedback": "# Отчёт\n\n## Вердикт: HIRE\n- Confidence: 75%"
    }
