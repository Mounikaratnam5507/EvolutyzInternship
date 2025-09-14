
# eval.py — Tiny evaluation harness for retrieval + answers
import json
from dotenv import load_dotenv
from ingest import build_vectorstore_from_uploads
from agent import build_agent_executor, get_retriever_tool, get_db_tools

load_dotenv()

def run_eval(files, questions):
    vs, retriever, _ = build_vectorstore_from_uploads(files)
    tools = [get_retriever_tool(retriever)] + get_db_tools()
    agent = build_agent_executor(tools)

    results = []
    for q in questions:
        out = agent.invoke({"input": q})
        results.append({"question": q, "answer": out.get("output","")})
    return results

if __name__ == "__main__":
    from pathlib import Path
    sample = Path("sample_docs/sample_policy.docx").open("rb")
    questions = [
        "What is the return policy?",
        "How long for refunds?",
        "Do you ship internationally?",
        "How do I reset my password?",
        "Where is my order 1002?"
    ]
    results = run_eval([sample], questions)
    print(json.dumps(results, indent=2))
