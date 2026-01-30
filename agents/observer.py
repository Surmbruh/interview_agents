from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from state import AgentState, ObserverOutput
from config import settings
from utils.llm_utils import llm_retry

class ObserverAgent:
    def __init__(self, model: ChatOpenAI):
        self.model = model
        self.system_prompt = """You are a Senior Technical Lead and Interview Observer. 
Your goal is to silently analyze the candidate's performance and guide the Interviewer.
**The interview is conducted in Russian.**

## CONTEXT AWARENESS (CRITICAL)
You will receive:
1. Recent conversation history (last 5 messages)
2. Previous analysis decisions you made
3. The latest user response

**DO NOT ask about topics already discussed. Review the conversation history carefully.**

## CRITICAL SCENARIOS TO DETECT:

1. **Hallucinations**: Did the user say something confidently false or nonsensical (e.g., "Python 4.0 replaces loops with neural links")?
   - If YES -> Decision: MAINTAIN. Instruction: "Politely correct the user's hallucination. Mark this topic as failed. Move to a simpler question."

2. **Role Reversal**: Did the user ask YOU a question (e.g., "What is your tech stack?")?
   - If YES -> Decision: MAINTAIN. Instruction: "Answer the user's question briefly and professionally, then steer back to the interview."

3. **Stop Command**: Did the user express a desire to end the interview (e.g., "Stop", "Enough", "Finish", "Хватит", "Закончили", "Стоп игра")?
   - If YES -> Decision: DECREASE_DIFFICULTY. Instruction: "Politely conclude the interview and thank the candidate."

4. **Off-topic Attempt**: Did the user try to change the subject or avoid answering (e.g., talking about weather, personal life, unrelated topics)?
   - If YES -> Decision: MAINTAIN. Instruction: "Politely acknowledge but redirect back to the technical interview. Ask the same or a related question."

5. **Standard Analysis** (if none above):
   - Accuracy: Is the answer technically correct?
   - Depth: Is it shallow or deep?
   - Confidence: Does the user sound confident or uncertain?
   - If uncertain -> Consider asking a follow-up or simpler question on the same topic

Based on this, decide:
- Difficulty: Should the next question be harder (if doing well) or simpler (if struggling)?
- Instruction: What specifically should the Interviewer ask next? MUST be a NEW topic not yet covered.

## TOPICS TRACKING
Keep mental track of covered topics. Suggest questions on NEW areas like:
- System Design, Databases, APIs, Testing, CI/CD, Security, Performance, Code Quality, etc.
"""

    @llm_retry
    def run(self, state: AgentState) -> dict:
        messages = state["messages"]
        candidate_info = state["candidate_info"]
        loop_count = state.get("loop_count", 0)
        
        # Check Context from Router
        router_decision = state.get("router_decision", "ANSWER")
        
        if router_decision != "ANSWER" and messages:
             return {"internal_thoughts": [], "topics_covered": state.get("topics_covered", [])}

        if loop_count >= 11:
            return {
                "internal_thoughts": [{
                    "analysis": "Question limit reached.",
                    "decision": "DECREASE_DIFFICULTY",
                    "instruction": "Thank the candidate and conclude the interview.",
                    "should_stop": True
                }]
            }

        # If no messages yet
        if not messages:
             initial_thought = {
                "analysis": "Start of interview.",
                "decision": "MAINTAIN",
                "instruction": f"Start the interview for a {candidate_info.get('Grade')} {candidate_info.get('Position')} role. Ask an introductory question."
            }
             # Manually creating dict to match old behavior, though we could use Pydantic here too
             return {"internal_thoughts": [initial_thought]}

        last_user_message = messages[-1].content
        
        # Build recent conversation context (last 5 messages)
        recent_messages = messages[-5:] if len(messages) > 5 else messages
        conversation_context = "\n".join([
            f"{'User' if hasattr(m, 'type') and m.type == 'human' else 'Interviewer'}: {m.content}"
            for m in recent_messages
        ])
        
        # Build previous analysis context
        previous_thoughts = state.get("internal_thoughts", [])
        topic_plan = state.get("topic_plan", [])
        
        previous_analysis = ""
        if previous_thoughts:
            recent_thoughts = previous_thoughts[-3:] if len(previous_thoughts) > 3 else previous_thoughts
            previous_analysis = "\n".join([
                f"- Decision: {t.get('decision', 'N/A')}, Topics: {t.get('topics_covered', [])}"
                for t in recent_thoughts if isinstance(t, dict)
            ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt + "\n\n**TOPIC PLAN**: {topic_plan}\nUse the plan above to decide the next topic. Do NOT repeat topics."),
            ("human", """Candidate Info: {candidate_info}

## Recent Conversation (last 5 messages):
{conversation_context}

## Previous Analysis Decisions:
{previous_analysis}

## Latest User Response to Analyze:
{last_user_message}""")
        ])
        
        # Use Structured Output
        structured_llm = self.model.with_structured_output(ObserverOutput)
        chain = prompt | structured_llm
        
        # Invoke LLM
        response: ObserverOutput = chain.invoke({
            "candidate_info": str(candidate_info),
            "topic_plan": ", ".join(topic_plan),
            "conversation_context": conversation_context,
            "previous_analysis": previous_analysis if previous_analysis else "No previous analysis yet.",
            "last_user_message": last_user_message
        })
        
        # Convert Pydantic to Dict for state
        thought_data = response.model_dump()
            
        return {
            "internal_thoughts": [thought_data],
            "topics_covered": thought_data.get("topics_covered", []),
            "current_turn_thoughts": {"Observer": thought_data["analysis"]}
        }
