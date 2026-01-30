from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from state import AgentState
import json


class ManagerAgent:
    """
    Senior Hiring Manager Agent.
    Responsible for making the final hiring decision based on Observer's analysis
    and the interview transcript. This agent does NOT interact with the candidate directly.
    
    Role Specialization:
    - Observer: Analyzes responses, detects issues, guides Interviewer
    - Interviewer: Conducts the conversation with the candidate
    - Manager: Makes the final hiring decision (this agent)
    """
    
    def __init__(self, model: ChatOpenAI):
        self.model = model
        self.system_prompt = """You are a Senior Hiring Manager at a top tech company.
Your role is to make the FINAL hiring decision based on:
1. The interview transcript
2. The Observer's analysis and notes
3. The candidate's stated experience and grade

**You MUST write your decision in Russian. DO NOT use any emojis or emoticons in your response.**

## EVALUATION CRITERIA

### Technical Skills (60% weight)
- Depth of knowledge in core technologies
- Problem-solving approach
- System design understanding
- Code quality awareness

### Soft Skills (20% weight)
- Communication clarity
- Honesty about limitations
- Engagement level
- Professionalism

### Red Flags (20% weight - negative)
- Hallucinations (confidently stating false information)
- Evasiveness or off-topic attempts
- Inconsistencies with stated experience

## DECISION CATEGORIES

1. **STRONG_HIRE** (90-100%): Exceptional candidate, exceeded expectations for the grade
2. **HIRE** (70-89%): Solid candidate, meets expectations for the grade
3. **MAYBE** (50-69%): Borderline, some concerns but potential
4. **NO_HIRE** (30-49%): Does not meet expectations for the stated grade
5. **STRONG_NO_HIRE** (0-29%): Significant issues, red flags detected

## OUTPUT FORMAT (JSON)
{{
  "decision": "HIRE" | "NO_HIRE" | "STRONG_HIRE" | "STRONG_NO_HIRE" | "MAYBE",
  "confidence_score": 0-100,
  "grade_assessment": "Matches stated grade" | "Above grade" | "Below grade",
  "soft_skills_analysis": {{
      "clarity": "Rating (1-10) and brief comment",
      "honesty": "Did candidate admit ignorance? (Yes/No/Partial)",
      "engagement": "Did candidate ask questions? (High/Medium/Low)"
  }},
  "key_strengths": ["list", "of", "strengths"],
  "key_concerns": ["list", "of", "concerns"],
  "recommendation": "Detailed recommendation text in Russian..."
}}
"""

    def evaluate(self, state: AgentState) -> dict:
        """
        Evaluate the candidate and return a hiring decision.
        This is called at the end of the interview to generate the final verdict.
        """
        messages = state.get("messages", [])
        internal_thoughts = state.get("internal_thoughts", [])
        candidate_info = state.get("candidate_info", {})
        interview_log = state.get("interview_log", [])
        
        # Format interview transcript
        transcript = ""
        for turn in interview_log:
            user_input = turn.get("user_input", "")
            agent_response = turn.get("agent_response", "")
            if user_input:
                transcript += f"Candidate: {user_input}\n"
            if agent_response:
                transcript += f"Interviewer: {agent_response}\n"
            transcript += "---\n"
        
        # Format observer notes
        observer_notes = []
        for thought in internal_thoughts:
            if isinstance(thought, dict):
                analysis = thought.get("analysis", "")
                decision = thought.get("decision", "")
                if analysis:
                    observer_notes.append(f"- {decision}: {analysis}")
        
        observer_summary = "\n".join(observer_notes) if observer_notes else "No detailed notes available."
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", """## Candidate Information
{candidate_info}

## Interview Transcript
{transcript}

## Observer's Analysis Notes
{observer_notes}

Based on all the above, provide your final hiring decision.""")
        ])
        
        chain = prompt | self.model
        
        response = chain.invoke({
            "candidate_info": str(candidate_info),
            "transcript": transcript,
            "observer_notes": observer_summary
        })
        
        # Parse the response
        try:
            content = response.content.replace("```json", "").replace("```", "").strip()
            decision_data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback if LLM fails to produce valid JSON
            decision_data = {
                "decision": "UNABLE_TO_EVALUATE",
                "confidence_score": 0,
                "grade_assessment": "Unable to assess",
                "key_strengths": [],
                "key_concerns": ["Failed to parse LLM response"],
                "recommendation": response.content,
                "raw_output": response.content
            }
        
        return decision_data

    def format_decision_report(self, decision_data: dict) -> str:
        """
        Format the decision data into a human-readable report.
        """
        decision = decision_data.get("decision", "UNKNOWN")
        confidence = decision_data.get("confidence_score", 0)
        grade_assessment = decision_data.get("grade_assessment", "N/A")
        strengths = decision_data.get("key_strengths", [])
        concerns = decision_data.get("key_concerns", [])
        recommendation = decision_data.get("recommendation", "")
        
        soft_skills = decision_data.get("soft_skills_analysis", {})
        ss_clarity = soft_skills.get("clarity", "N/A")
        ss_honesty = soft_skills.get("honesty", "N/A")
        ss_engagement = soft_skills.get("engagement", "N/A")
        
        report = f"""
## Решение Hiring Manager

### Решение: **{decision}**
- **Уверенность**: {confidence}%
- **Оценка грейда**: {grade_assessment}

### Soft Skills & Communication
- **Clarity (Ясность)**: {ss_clarity}
- **Honesty (Честность)**: {ss_honesty}
- **Engagement (Вовлечённость)**: {ss_engagement}

### Ключевые сильные стороны
{chr(10).join(['- ' + s for s in strengths]) if strengths else '- Не выявлено'}

### Ключевые замечания
{chr(10).join(['- ' + c for c in concerns]) if concerns else '- Не выявлено'}

### Рекомендация
{recommendation}
"""
        return report
