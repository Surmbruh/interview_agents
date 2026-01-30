"""
LangGraph definition for Multi-Agent Interview Coach.
Defines the cyclic graph with nodes for each agent and routing logic.
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from state import AgentState
from agents.interviewer import InterviewerAgent
from agents.observer import ObserverAgent
from agents.planner import planner_node
from agents.critic import critic_node
from router import router_node
from feedback import feedback_node
from config import settings
from utils.log_config import get_logger

# Setup logger for graph
logger = get_logger("graph")

# Load environment variables
load_dotenv()

# Initialize Models
api_base = settings.OPENAI_API_BASE
llm_observer = ChatOpenAI(model=settings.MODEL_OBSERVER, temperature=0, base_url=api_base)
llm_interviewer = ChatOpenAI(model=settings.MODEL_INTERVIEWER, temperature=0.7, base_url=api_base)

# Initialize Agents
observer_agent = ObserverAgent(llm_observer)
interviewer_agent = InterviewerAgent(llm_interviewer)


# Node Wrappers
def planner_node_wrapper(state: AgentState):
    """Executes Planner Logic once"""
    if state.get("topic_plan"):
        logger.debug("Topic plan already exists, skipping planner")
        return {"topic_plan": state["topic_plan"]}
    return planner_node(state)


def observer_node_wrapper(state: AgentState):
    """Executes Observer Agent Logic"""
    logger.info("Observer analyzing response...")
    return observer_agent.run(state)


def interviewer_node_wrapper(state: AgentState):
    """Executes Interviewer Agent Logic"""
    logger.info("Interviewer generating question...")
    return interviewer_agent.run(state)


def critic_node_wrapper(state: AgentState):
    """Executes Critic Logic and manages retries"""
    result = critic_node(state)
    
    # Track retries for the loop
    current_retry = state.get("critic_retry_count", 0)
    if result["critic_status"] == "REJECTED":
        return {**result, "critic_retry_count": current_retry + 1}
    else:
        return {**result, "critic_retry_count": 0}  # Reset on success


# Conditional Logic for Router
def route_next_step(state: AgentState):
    decision = state.get("router_decision", "ANSWER")
    
    if decision == "STOP":
        return "feedback"
    elif decision == "ANSWER":
        return "observer"
    elif decision in ["ROLE_REVERSAL", "INJECTION"]:
        return "interviewer"
    else:
        return "observer"


# Conditional Logic for Quality Loop
def route_critic_decision(state: AgentState):
    status = state.get("critic_status", "APPROVED")
    retry_count = state.get("critic_retry_count", 0)
    
    if status == "REJECTED" and retry_count < 2:
        logger.warning("Re-generating question (Attempt %d/2)...", retry_count + 1)
        return "interviewer"
    
    return END


# Build the Graph
builder = StateGraph(AgentState)

# Add Nodes
builder.add_node("planner", planner_node_wrapper)
builder.add_node("router", router_node)
builder.add_node("observer", observer_node_wrapper)
builder.add_node("interviewer", interviewer_node_wrapper)
builder.add_node("critic", critic_node_wrapper)
builder.add_node("feedback", feedback_node)

# Set Entry Point
builder.set_entry_point("planner")

# Define Edges
builder.add_edge("planner", "router")

builder.add_conditional_edges(
    "router",
    route_next_step,
    {
        "feedback": "feedback",
        "observer": "observer",
        "interviewer": "interviewer"
    }
)

builder.add_edge("observer", "interviewer")

# Quality Loop: Interviewer -> Critic -> [End | Interviewer]
builder.add_edge("interviewer", "critic")

builder.add_conditional_edges(
    "critic",
    route_critic_decision,
    {
        "interviewer": "interviewer",
        END: END
    }
)

builder.add_edge("feedback", END)

# Compile
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    from utils.log_config import setup_logging
    setup_logging("DEBUG")
    logger.info("Graph compiled successfully")
    print(graph.get_graph().draw_ascii())
