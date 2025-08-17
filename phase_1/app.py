import streamlit as st
from chatbot import chat_with_gpt
from summarize import summarize_text

# Page config
st.set_page_config(page_title="AI Chatbot & Summarizer", page_icon="🤖", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
    }
    .title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .subtitle {
        text-align: center;
        font-size: 16px;
        color: #666;
        margin-bottom: 20px;
    }
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        border-radius: 10px;
        background-color: #f5f5f5;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #DCF8C6;
        text-align: right;
        padding: 10px;
        border-radius: 15px;
        margin: 5px;
        margin-left: 20%;
    }
    .bot-message {
        background-color: #FFFFFF;
        text-align: left;
        padding: 10px;
        border-radius: 15px;
        margin: 5px;
        margin-right: 20%;
        box-shadow: 0px 1px 2px rgba(0,0,0,0.1);
    }
    .stTextInput>div>div>input, .stTextArea textarea {
        border-radius: 10px;
    }
    .stButton>button {
        border-radius: 10px;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<p class='title'>🤖 AI Chatbot & Summarizer</p>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Chat with GPT or Summarize your text instantly</p>", unsafe_allow_html=True)

# Sidebar choice
option = st.sidebar.radio("📌 Choose your tool:", ["Chatbot", "Summarizer"])

# ---------------- CHATBOT ----------------
if option == "Chatbot":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("💬 Chat with GPT")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

    # Display chat bubbles (skip system message)
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            st.markdown(f"<div class='bot-message'>{msg['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # User input
    user_input = st.text_input("Type your message...", key="input")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Send") and user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Get GPT response (send full history)
            response = chat_with_gpt(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": response})

            st.rerun()

    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SUMMARIZER ----------------
elif option == "Summarizer":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("📝 Text Summarizer")

    text = st.text_area("Enter text to summarize:", height=150, placeholder="Paste your paragraph here...")
    if st.button("Summarize") and text:
        summary = summarize_text(text)
        st.success(summary)

    st.markdown("</div>", unsafe_allow_html=True)
