
# db_tools.py — SQLite DB tools for the agent
import os, sqlite3

DB_PATH = os.path.join("db", "sample.db")

def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def find_order(order_id: int) -> str:
    """Return a friendly one-line order status summary for the given order id."""
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("SELECT order_id, customer, status, total FROM orders WHERE order_id = ?", (order_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return f"No order found with id {order_id}."
        oid, cust, status, total = row
        return f"Order {oid} for {cust}: status {status}, total {total:.2f}."
    except Exception as e:
        return f"DB error: {e}"

def search_faq(query: str) -> str:
    """Return top matching FAQs for the query."""
    try:
        conn = _connect()
        cur = conn.cursor()
        q = f"%{query}%"
        cur.execute("SELECT question, answer FROM faqs WHERE question LIKE ? OR answer LIKE ? LIMIT 5", (q,q))
        rows = cur.fetchall()
        conn.close()
        if not rows:
            return "No FAQ results."
        return "\n".join([f"{i+1}. {q} → {a}" for i,(q,a) in enumerate(rows)])
    except Exception as e:
        return f"DB error: {e}"
