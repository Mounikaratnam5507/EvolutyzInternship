
# Phase 2 — LangChain RAG + DB + Telemetry

**Focus:** Agent architectures, LangChain, RAG pipelines, tool calling, memory, DB integration  
**Core Skills:** LangChain chains & agents, vector stores, embeddings, tool integration, eval & logging  
**Capstone Output:** Document Q&A / Customer Support Agent with **RAG + DB + telemetry**

## Folder Layout
```
app.py                 # Streamlit UI (Upload & Build only in sidebar; Tabs: Chat / Documents / Telemetry)
ingest.py              # Load files, split text, OpenAI embeddings, FAISS vector store
agent.py               # LangChain agent (ChatOpenAI + tools + memory)
db_tools.py            # SQLite tools (find_order, search_faq)
telemetry.py           # CSV logging
seed_db.py             # Seeds db/sample.db with orders + FAQs
eval.py                # Tiny evaluation harness
sample_docs/sample_policy.docx
.streamlit/config.toml # Theme
requirements.txt
.env.example           # Example env vars
.gitignore
```

## Quickstart
```bash
# 1) Create & activate venv
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Configure API key
cp .env.example .env
# edit .env to put your key: OPENAI_API_KEY=sk-...

# 4) Seed the sample SQLite DB
python seed_db.py





## Notes
- Uses OpenAI embeddings (text-embedding-3-small) and ChatOpenAI (gpt-4o-mini) via langchain-openai.
- Requires OPENAI_API_KEY in env or .env file.
- Telemetry is logged to logs/chat_log.csv.
