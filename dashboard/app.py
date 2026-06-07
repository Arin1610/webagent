import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from agent.react_agent import run_agent
from agent.memory import ConversationMemory

st.set_page_config(
    page_title="WebAgent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 WebAgent — Autonomous AI Research Agent")
st.markdown("Ask any question and watch the agent search the web, scrape pages, and synthesize answers in real time.")

# Initialize memory in session state
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Agent Settings")
    max_steps = st.slider("Max reasoning steps", 1, 8, 5)
    
    st.divider()
    st.markdown("## 🧠 How it works")
    st.markdown("""
    1. You ask a question
    2. Agent **thinks** about what to search
    3. Agent **searches** DuckDuckGo
    4. Agent **scrapes** relevant pages
    5. Agent **synthesizes** a final answer
    
    This is the **ReAct** pattern:
    **Re**asoning + **Act**ing
    """)
    
    st.divider()
    if st.button("🗑️ Clear conversation"):
        st.session_state.memory.clear()
        st.session_state.chat_history = []
        st.rerun()

# Display chat history
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["question"])
    
    with st.chat_message("assistant"):
        st.write(chat["answer"])
        
        # Show reasoning steps in expander
        with st.expander(f"🔍 View reasoning steps ({chat['total_steps']} steps)"):
            for step in chat["steps"]:
                if step["type"] == "tool_call":
                    st.markdown(f"**Step {step['step']} — {step['action']}**")
                    st.code(step["input"], language="text")
                    st.markdown("**Result preview:**")
                    st.text(step["result"][:300])
                    st.divider()
                elif step["type"] == "final":
                    st.markdown(f"**Step {step['step']} — Final Answer**")

# Chat input
question = st.chat_input("Ask me anything — I'll research it for you...")

if question:
    with st.chat_message("user"):
        st.write(question)
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 Agent is researching..."):
            # Add memory context to question
            context = st.session_state.memory.get_context()
            full_question = f"{context}\nCurrent question: {question}" if context else question
            
            result = run_agent(full_question, max_iterations=max_steps)
        
        st.write(result["answer"])
        
        with st.expander(f"🔍 View reasoning steps ({result['total_steps']} steps)"):
            for step in result["steps"]:
                if step["type"] == "tool_call":
                    st.markdown(f"**Step {step['step']} — {step['action']}**")
                    st.code(step["input"], language="text")
                    st.markdown("**Result preview:**")
                    st.text(step["result"][:300])
                    st.divider()
                elif step["type"] == "final":
                    st.markdown(f"**Step {step['step']} — Final Answer**")
        
        # Save to memory and history
        st.session_state.memory.add_turn(question, result["answer"])
        st.session_state.chat_history.append({
            "question": question,
            "answer": result["answer"],
            "steps": result["steps"],
            "total_steps": result["total_steps"]
        })