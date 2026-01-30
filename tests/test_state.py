"""
Tests for State validation and Pydantic schemas.
"""
import pytest
from pydantic import ValidationError


class TestPydanticSchemas:
    """Test Pydantic output schemas for structured LLM outputs."""
    
    def test_observer_output_valid(self):
        """ObserverOutput should accept valid data."""
        from state import ObserverOutput
        
        output = ObserverOutput(
            analysis="Candidate answered correctly about GIL",
            decision="INCREASE_DIFFICULTY",
            instruction="Ask about asyncio and coroutines",
            topics_covered=["GIL", "Threading"],
            should_stop=False
        )
        
        assert output.decision == "INCREASE_DIFFICULTY"
        assert "GIL" in output.topics_covered
    
    def test_observer_output_defaults(self):
        """ObserverOutput should have correct defaults."""
        from state import ObserverOutput
        
        output = ObserverOutput(
            analysis="Basic analysis",
            decision="MAINTAIN",
            instruction="Continue"
        )
        
        assert output.topics_covered == []
        assert output.should_stop is False
    
    def test_interviewer_output_valid(self):
        """InterviewerOutput should accept valid data."""
        from state import InterviewerOutput
        
        output = InterviewerOutput(
            response_text="Расскажите про ваш опыт с Docker.",
            topic_status="ongoing"
        )
        
        assert "Docker" in output.response_text
        assert output.topic_status == "ongoing"
    
    def test_critic_output_approved(self):
        """CriticOutput should handle APPROVED status."""
        from state import CriticOutput
        
        output = CriticOutput(
            status="APPROVED",
            feedback=""
        )
        
        assert output.status == "APPROVED"
    
    def test_critic_output_rejected_with_feedback(self):
        """CriticOutput REJECTED should include feedback."""
        from state import CriticOutput
        
        output = CriticOutput(
            status="REJECTED",
            feedback="Вопрос слишком простой для Senior грейда"
        )
        
        assert output.status == "REJECTED"
        assert "Senior" in output.feedback


class TestAgentStateStructure:
    """Test AgentState TypedDict structure."""
    
    def test_agent_state_has_required_fields(self):
        """AgentState should define all required fields."""
        from state import AgentState
        
        required_fields = [
            "messages",
            "candidate_info", 
            "company_profile",
            "internal_thoughts",
            "interview_log",
            "loop_count",
            "topics_covered",
            "router_decision",
            "topic_plan",
            "critic_feedback",
            "critic_retry_count",
            "current_question",
            "current_turn_thoughts",
            "session_id"
        ]
        
        annotations = AgentState.__annotations__
        
        for field in required_fields:
            assert field in annotations, f"Missing field: {field}"
