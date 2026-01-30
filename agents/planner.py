from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List
import os
from state import AgentState
from config import settings
from utils.llm_utils import llm_retry

class PlanOutput(BaseModel):
    """Structured output for the Interview Planner."""
    topics: List[str] = Field(..., description="List of 4-5 technical topics to cover during the interview.")
    reasoning: str = Field(..., description="Brief explanation of why these topics were chosen.")

@llm_retry
def planner_node(state: AgentState):
    """
    Planner Node: Generates a technical interview plan based on candidate grade and position.
    Runs once at the beginning of the session.
    """
    candidate_info = state["candidate_info"]
    company_profile = state.get("company_profile", "")
    
    # Initialize LLM using settings
    api_base = settings.OPENAI_API_BASE
    llm = ChatOpenAI(model=settings.MODEL_ROUTER, temperature=0, base_url=api_base)
    
    # Structured output
    structured_llm = llm.with_structured_output(PlanOutput)
    
    system_prompt = """You are a Technical Interview Planner.
Your task is to create a structured interview plan for a specific candidate.

Analyze the Candidate's Grade, Position, and the Company Profile.
Generate exactly 4-5 specific technical topics that should be verified.

Topics should be:
1. Relevant to the position and grade.
2. Specific (not just "Python", but "GIL and Concurrency" or "Memory Management").
3. Aligned with the company's tech stack if provided.
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Candidate Info: {candidate_info}\nCompany Profile: {company_profile}")
    ])
    
    chain = prompt | structured_llm
    
    print(f"--- Planning Interview Session for {candidate_info.get('Grade')} {candidate_info.get('Position')} ---")
    
    response: PlanOutput = chain.invoke({
        "candidate_info": str(candidate_info),
        "company_profile": company_profile
    })
    
    print(f"--- Topic Plan: {', '.join(response.topics)} ---")
    
    return {"topic_plan": response.topics}
