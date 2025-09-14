# app.py
import streamlit as st
from chatbot import chat_with_gpt
from summarize import summarize_text

# -------------------- Page Setup --------------------
st.set_page_config(
    page_title="AI Chatbot & Summarizer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- Global Styles --------------------
st.markdown("""
<style>
/* App background */
.stApp { background: linear-gradient(120deg, #f6f7fb 0%, #eef2f7 100%); }

/* Sidebar look */
section[data-testid="stSidebar"] {
  background: #0f172a; /* dark slate */
  color: #e2e8f0;
  border-right: 1px solid #1f2937;
}
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] p, 
section[data-testid="stSidebar"] label {
  color: #e2e8f0 !important;
}

/* Main header card */
.header-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 16px 20px;
  box-shadow: 0 6px 24px rgba(15, 23, 42, .06);
  margin-bottom: 16px;
}

/* Content card */
.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 12px 16px;
  box-shadow: 0 8px 30px rgba(2,6,23,.06);
}

/* Buttons */
.stButton > button {
  background: #6366f1 !important;
  color: white !important;
  border-radius: 10px !important;
  border: none !important;
  font-weight: 600 !important;
  padding: 0.5rem 0.9rem !important;
}
.stButton > button:hover { background: #4f46e5 !important; }

/* Inputs */
textarea, .stTextInput input {
  border-radius: 10px !important;
  border: 1px solid #e5e7eb !important;
}

/* Chat container sizing */
.chat-wrap {
  height: calc(100vh - 240px);
  overflow-y: auto;
  padding: 6px 0;
}

/* Small helper text */
.label { font-size: 13px; color: #64748b; }

/* ---- IMPORTANT: remove any divider visuals, even if present ---- */
.divider { display:none !important; height:0 !important; margin:0 !important; border:none !important; background:transparent !important; }
hr { display:none !important; }
</style>
""", unsafe_allow_html=True)

# -------------------- Sidebar (Left Nav) --------------------
with st.sidebar:
    st.markdown("## 🤖 AI Studio")
    st.caption("Classic, clean, and fast.")

    nav = st.radio(
        "Navigation",
        options=["Chatbot", "Summarizer"],
        index=0,
        label_visibility="collapsed",
    )

    st.subheader("⚙️ Settings")
    system_prompt = st.text_area(
        "System prompt",
        value=st.session_state.get("system_prompt", "You are a helpful, concise assistant."),
        height=90,
    )
    st.session_state["system_prompt"] = system_prompt

    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        if st.button("🧹 Clear All"):
            st.session_state["chat_messages"] = [{"role": "system", "content": system_prompt}]
            st.session_state.pop("summary", None)
            st.success("Cleared.")
            st.rerun()
    with col_sb2:
        if st.button("♻️ Reset Prompt"):
            st.session_state["system_prompt"] = "You are a helpful, concise assistant."
            st.rerun()

# -------------------- Session State --------------------
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [{"role": "system", "content": st.session_state["system_prompt"]}]

# -------------------- Single Header (no divider below) --------------------
if nav == "Chatbot":
    st.markdown(
        """
        <div class="header-card">
          <h2 style="margin:0;">💬 Chatbot</h2>
         
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="header-card">
          <h2 style="margin:0;">📝 Summarizer</h2>
                 </div>
        """,
        unsafe_allow_html=True,
    )

# ====================== CHATBOT ======================
if nav == "Chatbot":
    # st.markdown("<div class='card'>", unsafe_allow_html=True)

    # Chat history
    st.markdown("<div class='chat-wrap'>", unsafe_allow_html=True)
    for msg in st.session_state["chat_messages"]:
        if msg["role"] == "system":
            continue
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])
    st.markdown("</div>", unsafe_allow_html=True)

    # Clear button
    if st.button("Clear chat"):
        st.session_state["chat_messages"] = [{"role": "system", "content": st.session_state["system_prompt"]}]
        st.rerun()

    # Chat input
    user_text = st.chat_input("Type your message…")
    if user_text:
        st.session_state["chat_messages"].append({"role": "user", "content": user_text})

        payload = st.session_state["chat_messages"].copy()
        if payload and payload[0]["role"] == "system":
            payload[0]["content"] = st.session_state["system_prompt"]
        else:
            payload.insert(0, {"role": "system", "content": st.session_state["system_prompt"]})

        with st.spinner("Thinking…"):
            reply = chat_with_gpt(payload)

        st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ===================== SUMMARIZER ====================
else:
    # st.markdown("<div class='card'>", unsafe_allow_html=True)

    # NOTE: No second heading here (prevents duplicate title)
    st.markdown("<span class='label'>Paste any text and get a concise summary.</span>", unsafe_allow_html=True)

    text = st.text_area("Input text", height=220, placeholder="Paste paragraph(s) to summarize…")

    c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
    with c1:
        summarize_now = st.button("✅ Summarize")
    with c2:
        if st.button("🗑️ Clear"):
            st.session_state.pop("summary", None)
            st.rerun()
    with c3:
        if st.session_state.get("summary"):
            st.download_button(
                "⬇️ Download",
                data=st.session_state["summary"].encode("utf-8"),
                file_name="summary.txt",
                mime="text/plain",
            )

    if summarize_now and text.strip():
        with st.spinner("Summarizing…"):
            st.session_state["summary"] = summarize_text(text)

    if st.session_state.get("summary"):
        st.markdown(
            f"""
            <div style="
                background:#f0fdf4; 
                border:1px solid #bbf7d0; 
                color:#064e3b; 
                padding:14px 16px; 
                border-radius:12px;
                margin-top:12px;">
                {st.session_state['summary']}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
