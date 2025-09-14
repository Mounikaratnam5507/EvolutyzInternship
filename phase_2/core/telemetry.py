
# telemetry.py — CSV telemetry logger
import os, json
import pandas as pd

LOG_PATH = os.path.join("logs", "chat_log.csv")

def ensure_log_headers():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    if not os.path.exists(LOG_PATH):
        pd.DataFrame(columns=["ts","user","assistant","used_db","top_docs"]).to_csv(LOG_PATH, index=False)

def log_turn(user_msg: str, assistant_msg: str, used_db: bool, top_docs):
    ensure_log_headers()
    row = {
        "ts": pd.Timestamp.utcnow().isoformat(),
        "user": user_msg,
        "assistant": assistant_msg,
        "used_db": used_db,
        "top_docs": json.dumps(top_docs[:3], ensure_ascii=False)
    }
    df = pd.DataFrame([row])
    df.to_csv(LOG_PATH, mode="a", header=False, index=False)
