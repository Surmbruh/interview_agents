from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState
import os


def generate_final_report(state: AgentState) -> str:
    """
    Generates a comprehensive interview report using a multi-agent approach:
    1. ManagerAgent makes the hiring decision
    2. Report generator creates the detailed feedback
    
    This ensures proper role specialization:
    - Observer analyzed responses during the interview
    - Interviewer conducted the conversation
    - Manager makes the final decision
    - Report generator compiles everything
    """
    messages = state.get("messages", [])
    internal_thoughts = state.get("internal_thoughts", [])
    candidate_info = state.get("candidate_info", {})
    interview_log = state.get("interview_log", [])
    
    # Initialize LLMs
    api_base = os.getenv("OPENAI_API_BASE")
    llm = ChatOpenAI(model="openai/gpt-4o", temperature=0, base_url=api_base)
    
    # Import and use ManagerAgent for the hiring decision
    from agents.manager import ManagerAgent
    manager = ManagerAgent(llm)
    
    # Get Manager's decision
    print("    → Manager Agent is evaluating the candidate...")
    manager_decision = manager.evaluate(state)
    manager_report = manager.format_decision_report(manager_decision)
    
    # Generate detailed technical report
    technical_report = generate_technical_report(state, llm)
    
    # Generate development roadmap
    roadmap = generate_development_roadmap(state, llm)
    
    # Combine all reports
    full_report = f"""
# Отчёт по техническому интервью

## Информация о кандидате
- **Имя**: {candidate_info.get('Name', 'N/A')}
- **Позиция**: {candidate_info.get('Position', 'N/A')}
- **Грейд**: {candidate_info.get('Grade', 'N/A')}
- **Опыт**: {candidate_info.get('Experience', 'N/A')}

{manager_report}

{technical_report}

{roadmap}

---
*Отчёт сгенерирован автоматически системой Multi-Agent Interview Coach*
"""
    
    return full_report


def generate_technical_report(state: AgentState, llm: ChatOpenAI) -> str:
    """
    Generates the technical assessment section of the report.
    """
    interview_log = state.get("interview_log", [])
    internal_thoughts = state.get("internal_thoughts", [])
    candidate_info = state.get("candidate_info", {})
    
    system_prompt = """You are a Technical Assessment Specialist.
Analyze the interview transcript and observer notes to create a detailed technical assessment.
**You MUST write in Russian. DO NOT use any emojis or emoticons in your analysis.**

Structure your assessment as:
1. Подтверждённые навыки (Confirmed Skills) - list specific topics where candidate was correct.
2. Выявленные пробелы (Knowledge Gaps) - topics where candidate failed or was unsure.
   **CRITICAL: For EACH gap, you MUST provide the Correct Answer/Explanation.**
   Format: "- Topic: Error... (Correct Answer: ...)"
3. Ключевые моменты (Key Moments) - best and worst answers.
"""
    
    # Format data
    transcript = ""
    for turn in interview_log:
        user_input = turn.get("user_input", "")
        agent_response = turn.get("agent_response", "")
        thoughts = turn.get("internal_thoughts", {})
        if user_input:
            transcript += f"Q: {agent_response}\nA: {user_input}\n"
            if isinstance(thoughts, dict):
                analysis = thoughts.get("analysis", "")
                if analysis:
                    transcript += f"[Analysis: {analysis}]\n"
            transcript += "---\n"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Candidate: {candidate_info}

Interview Q&A with Analysis:
{transcript}

Generate the technical assessment section.""")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "candidate_info": str(candidate_info),
        "transcript": transcript
    })
    
    return f"## Техническая оценка\n\n{response.content}"


def generate_development_roadmap(state: AgentState, llm: ChatOpenAI) -> str:
    """
    Generates a personalized development roadmap for the candidate.
    """
    interview_log = state.get("interview_log", [])
    internal_thoughts = state.get("internal_thoughts", [])
    candidate_info = state.get("candidate_info", {})
    
    system_prompt = """You are a Career Development Coach.
Based on the interview performance, create a personalized development roadmap.
**You MUST write in Russian. DO NOT use any emojis or emoticons.**

Structure the roadmap as:
1. Что изучить (What to Learn) - specific topics and resources
2. Полезные ресурсы (Resources) - **Provide links to official docs or high-quality articles for the identified gaps.**
3. Рекомендации по практике (Practice Recommendations) - projects, exercises
4. Краткосрочные цели (Next 1-3 months)

Be specific and actionable. Reference actual gaps identified in the interview.
"""
    
    # Collect gaps from observer thoughts
    gaps = []
    for thought in internal_thoughts:
        if isinstance(thought, dict):
            decision = thought.get("decision", "")
            if decision in ["DECREASE_DIFFICULTY", "MAINTAIN"]:
                analysis = thought.get("analysis", "")
                if analysis:
                    gaps.append(analysis)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Candidate: {candidate_info}

Identified Areas for Improvement:
{gaps}

Number of questions answered: {num_questions}

Generate the development roadmap section.""")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "candidate_info": str(candidate_info),
        "gaps": "\n".join([f"- {g}" for g in gaps]) if gaps else "No specific gaps identified.",
        "num_questions": len(interview_log)
    })
    
    return f"## План развития\n\n{response.content}"
