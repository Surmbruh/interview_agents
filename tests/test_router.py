"""
Tests for the Router (Guardrail) Node.
Tests the classification logic and edge cases.
"""
import pytest
from langchain_core.messages import HumanMessage


class TestRouterEmptyMessages:
    """Test router behavior with empty messages."""
    
    def test_empty_messages_returns_answer(self):
        """First turn with no messages should proceed as ANSWER."""
        from router import router_node
        
        state = {"messages": []}
        result = router_node(state)
        
        assert result["router_decision"] == "ANSWER"
    
    def test_empty_list_returns_answer(self):
        """Empty message list should be treated as initial turn."""
        from router import router_node
        
        state = {"messages": []}
        result = router_node(state)
        
        assert "router_decision" in result
        assert result["router_decision"] == "ANSWER"


class TestRouterDecisionTypes:
    """Test that router returns valid decision types."""
    
    def test_valid_decision_types(self):
        """Verify all valid decision types are defined."""
        valid_types = ["ANSWER", "STOP", "ROLE_REVERSAL", "INJECTION"]
        
        # Router should always return one of these
        from router import RouteResponse
        
        # Test that RouteResponse accepts valid types
        for decision_type in valid_types:
            response = RouteResponse(category=decision_type, reasoning="Test")
            assert response.category == decision_type
    
    def test_route_response_schema(self):
        """Test RouteResponse Pydantic model."""
        from router import RouteResponse
        
        response = RouteResponse(category="ANSWER", reasoning="Normal answer")
        assert response.category == "ANSWER"
        assert response.reasoning == "Normal answer"


class TestRouterIntegration:
    """Integration tests that require API (skipped if no key)."""
    
    @pytest.mark.skipif(
        not __import__('os').getenv('RUN_INTEGRATION_TESTS'),
        reason="Set RUN_INTEGRATION_TESTS=1 to run integration tests"
    )
    def test_stop_command_with_real_api(self):
        """Test STOP classification with real API (requires key)."""
        from router import router_node
        
        state = {"messages": [HumanMessage(content="Стоп игра")]}
        result = router_node(state)
        
        assert result["router_decision"] == "STOP"
