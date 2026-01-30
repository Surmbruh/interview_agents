import streamlit as st
import uuid
from langchain_core.messages import HumanMessage, AIMessage
from graph import graph
from dotenv import load_dotenv
import time

# Page Config
st.set_page_config(
    page_title="Multi-Agent Interview Coach",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphic CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        color: #e0e0e0;
    }
    .stApp {
        background: transparent;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(30, 30, 47, 0.9);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background: rgba(0, 122, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .agent-thought {
        font-size: 0.85em;
        color: #888;
        font-style: italic;
        border-left: 2px solid #555;
        padding-left: 10px;
        margin-top: 5px;
    }
    h1, h2, h3 { color: #fff !important; }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "finished" not in st.session_state:
    st.session_state.finished = False

# Sidebar: Configuration
with st.sidebar:
    st.title("🎓 Настройка сессии")
    scenario_id = st.number_input("Номер сценария (1-5)", min_value=1, max_value=5, value=1)
    
    st.subheader("👤 Кандидат")
    name = st.text_input("Имя", value="Данил")
    grade = st.selectbox("Грейд", ["Junior", "Middle", "Senior", "Lead"], index=1)
    position = st.text_input("Позиция", value="Python Backend Developer")
    
    st.divider()
    
    if st.button("🚀 Начать интервью", use_container_width=True, type="primary"):
        st.session_state.interview_started = True
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.finished = False
        
        # Initial State
        initial_state = {
            "messages": [],
            "candidate_info": {"Name": name, "Position": position, "Grade": grade, "Experience": "N/A"},
            "company_profile": "TechFin Solutions. Python 3.11, Django, FastAPI, PostgreSQL, AWS.",
            "internal_thoughts": [],
            "interview_log": [],
            "loop_count": 0,
            "topics_covered": [],
            "router_decision": "ANSWER",
            "topic_plan": [],
            "critic_feedback": "",
            "critic_retry_count": 0,
            "current_question": "",
            "current_turn_thoughts": {},
            "session_id": scenario_id
        }
        
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        
        with st.spinner("Планирование интервью..."):
            events = graph.invoke(initial_state, config)
            first_msg = events.get("messages", [])[-1].content
            st.session_state.messages.append({"role": "assistant", "content": first_msg})
        st.rerun()

    if st.button("🧹 Очистить чат", use_container_width=True):
        st.session_state.messages = []
        st.session_state.interview_started = False
        st.rerun()

# Main UI
st.title("🎤 Multi-Agent Interview Coach")
st.caption(f"Scenario #{scenario_id} | {grade} {position} | Thread: {st.session_state.thread_id}")

if not st.session_state.interview_started:
    st.info("👋 Добро пожаловать! Настройте параметры в боковой панели и нажмите 'Начать интервью'.")
else:
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "thoughts" in msg and msg["thoughts"]:
                with st.expander("👁️ Agent Thoughts"):
                    for agent, thought in msg["thoughts"].items():
                        st.markdown(f"**[{agent}]**: {thought}")

    # Chat Input
    if not st.session_state.finished:
        if prompt := st.chat_input("Ваш ответ..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Invoke Graph
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            current_state = {"messages": [HumanMessage(content=prompt)]}
            
            with st.chat_message("assistant"):
                thought_placeholder = st.empty()
                with st.status("Thinking...", expanded=False) as status:
                    st.write("🔍 Analyzing your response...")
                    # Invoke graph
                    events = graph.invoke(current_state, config)
                    status.update(label="Response generated!", state="complete", expanded=False)
                
                # Get response
                last_msg = events.get("messages", [])[-1].content
                
                if last_msg == "INTERVIEW_FINISHED":
                    st.session_state.finished = True
                    st.success("🏁 Интервью закончено. Генерация отчета...")
                    st.rerun()
                else:
                    # Collect turn thoughts
                    final_state = graph.get_state(config).values
                    thoughts = final_state.get("current_turn_thoughts", {})
                    
                    st.write(last_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": last_msg,
                        "thoughts": thoughts
                    })
                    st.rerun()

    else:
        # Show Final Report
        st.divider()
        st.header("📊 Финальный отчёт")
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        final_state = graph.get_state(config).values
        
        # Display the markdown report
        # The feedback_node saves the report in interview_log.json and sends INTERVIEW_FINISHED.
        # But we can reconstructed it or show where it is.
        st.success(f"Log saved as interview_log_{final_state.get('session_id')}.json")
        
        if st.button("🔄 Начать заново"):
            st.session_state.interview_started = False
            st.session_state.finished = False
            st.rerun()
