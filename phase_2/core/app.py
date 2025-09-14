# app.py — Phase 2 (LangChain): Document Q&A / Support Agent with RAG + DB + Telemetry
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from ingest import build_vectorstore_from_uploads
from agent import build_agent_executor, get_retriever_tool, get_db_tools
from telemetry import log_turn, ensure_log_headers, LOG_PATH

# Load env (.env)
load_dotenv()

APP_TITLE = "Phase 2 — LangChain RAG + DB + Telemetry"
st.set_page_config(page_title=APP_TITLE, page_icon="🧠", layout="wide")

# ------------- CSS -------------
st.markdown("""
<style>
html, body, [class*="css"] { font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial; }
.app-title { font-size: 1.6rem; font-weight: 800; margin-bottom: 0.1rem; }
.pill {display:inline-block;padding:2px 10px;border-radius:999px;background:#f6f6f7;border:1px solid #e5e7eb;margin-right:6px;font-size:0.8rem}
.chat-bubble-user { background:#eef6ff; border:1px solid #e5e7eb;border-radius:14px;padding:12px; }
.chat-bubble-ai { background:#f9fafb; border:1px solid #e5e7eb;border-radius:14px;padding:12px; }
.small {font-size:0.86rem; opacity:0.85}
</style>
""", unsafe_allow_html=True)

# ------------- Header -------------
left, right = st.columns([0.7, 0.3], vertical_alignment="center")
with left:
    st.markdown(f'<div class="app-title">🧠 {APP_TITLE}</div>', unsafe_allow_html=True)
    st.markdown('<span class="pill">LangChain</span><span class="pill">RAG</span><span class="pill">DB Tool</span><span class="pill">Telemetry</span>', unsafe_allow_html=True)
with right:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    with c2:
        if st.button("🗑️ Reset Index", use_container_width=True):
            st.session_state.vectorstore = None
            st.session_state.retriever_tool = None
            st.session_state.docs_meta = []
            st.toast("Index cleared", icon="🗑️")

# ------------- Sidebar (Upload & Build only) -------------
with st.sidebar:
    st.header("📄 Upload & Build")
    files = st.file_uploader("Upload files", type=["pdf", "docx", "txt", "md"], accept_multiple_files=True)
    build = st.button("🔧 Build / Rebuild Index", type="primary", disabled=not files)

# ------------- Session Init -------------
ensure_log_headers()
if "history" not in st.session_state:
    st.session_state.history = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "retriever_tool" not in st.session_state:
    st.session_state.retriever_tool = None
if "docs_meta" not in st.session_state:
    st.session_state.docs_meta = []  # list of {"file":..., "chars":..., "chunks":...}

# ------------- Build index -------------
if build and files:
    with st.status("Building index with embeddings...", expanded=False) as s:
        vs, retriever, docs_meta = build_vectorstore_from_uploads(files)
        st.session_state.vectorstore = vs
        st.session_state.retriever_tool = get_retriever_tool(retriever)
        st.session_state.docs_meta = docs_meta
        s.update(label="Index ready ✅", state="complete")
    st.success(f"Indexed {sum(m['chunks'] for m in st.session_state.docs_meta)} chunks from {len(st.session_state.docs_meta)} file(s).")

# ------------- Main Tabs -------------
tab_chat, tab_docs, tab_logs = st.tabs(["💬 Chat", "📑 Documents", "📈 Telemetry"])

with tab_docs:
    if st.session_state.docs_meta:
        df = pd.DataFrame(st.session_state.docs_meta).rename(columns={"file":"File","chars":"Chars","chunks":"Chunks"})
        st.dataframe(df.sort_values("File"), use_container_width=True, hide_index=True)
        st.caption(f"Total chunks: {df['Chunks'].sum()}")
        st.info("A sample doc is included in 'sample_docs/sample_policy.docx' for quick testing.")
    else:
        st.info("Upload files and build the index to see document stats.")

with tab_logs:
    st.caption("Last 20 turns (if any).")
    if os.path.exists(LOG_PATH):
        try:
            df = pd.read_csv(LOG_PATH)
            st.dataframe(df.tail(20), use_container_width=True, hide_index=True)
            with open(LOG_PATH, "rb") as f:
                st.download_button("⬇️ Download chat_log.csv", f, file_name="chat_log.csv")
        except Exception as e:
            st.warning(f"Could not read logs: {e}")
    else:
        st.info("No logs yet. Ask something in Chat.")

with tab_chat:
    # show history
    for t in st.session_state.history:
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-bubble-user">{t["user"]}</div>', unsafe_allow_html=True)
        with st.chat_message("assistant"):
            st.markdown(f'<div class="chat-bubble-ai">{t["assistant"]}</div>', unsafe_allow_html=True)
            if t.get("sources"):
                with st.expander("Sources used"):
                    for (title, score) in t["sources"]:
                        st.write(f"- {title}  (score: {score:.3f})")

    # chat input
    user_msg = st.chat_input("Ask about your docs or try: Where is my order 1002?")
    if user_msg:
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-bubble-user">{user_msg}</div>', unsafe_allow_html=True)

        if st.session_state.retriever_tool is None:
            st.warning("No index yet. Upload files and click Build / Rebuild Index.")
        else:
            db_tools = get_db_tools()
            tools = [st.session_state.retriever_tool] + db_tools

            try:
                agent_executor = build_agent_executor(tools)
            except Exception as e:
                st.error(f"Failed to initialize agent: {e}")
                st.stop()

            result = agent_executor.invoke({"input": user_msg})
            answer = result.get("output", "")
            interm = result.get("intermediate_steps", [])
            used_db = any(step.get("tool") in {"find_order", "search_faq"} for step in interm if isinstance(step, dict))

            try:
                retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 5})
                docs = retriever.invoke(user_msg)
                top_titles = [(d.metadata.get("source",""), float(d.metadata.get("score", 0.0))) for d in docs]
            except Exception:
                docs = []
                top_titles = []

            with st.chat_message("assistant"):
                st.markdown(f'<div class="chat-bubble-ai">{answer}</div>', unsafe_allow_html=True)
                if docs:
                    with st.expander("Sources used"):
                        for d in docs:
                            title = d.metadata.get("source", "chunk")
                            score = d.metadata.get("score", 0.0)
                            st.write(f"- {title} (score≈{score:.3f})")

            st.session_state.history.append({"user": user_msg, "assistant": answer, "sources": top_titles})
            st.session_state.history = st.session_state.history[-10:]
            log_turn(user_msg, answer, used_db=bool(used_db), top_docs=[d.page_content[:120] for d in docs])

