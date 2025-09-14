
# seed_db.py — Initialize sample DB with orders & FAQs
import os, sqlite3

DB_PATH = os.path.join("db","sample.db")
os.makedirs("db", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer TEXT,
    status TEXT,
    total REAL
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS faqs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT
)""")

orders = [
    (1001, "Alice", "Delivered", 129.99),
    (1002, "Bob", "Processing", 89.50),
    (1003, "Chandra", "Shipped", 59.00)
]
for oid, cust, st, total in orders:
    cur.execute("INSERT OR REPLACE INTO orders(order_id, customer, status, total) VALUES (?,?,?,?)",
                (oid, cust, st, total))

faqs = [
    ("What is the return policy?", "You can return items within 30 days in original condition."),
    ("How do I reset my password?", "Click 'Forgot password' on the login page and follow the email link."),
    ("Do you offer international shipping?", "Yes, to selected countries with additional fees."),
    ("How long does shipping take?", "Standard shipping takes 3-5 business days."),
]
for q,a in faqs:
    cur.execute("SELECT 1 FROM faqs WHERE question=?",(q,))
    if not cur.fetchone():
        cur.execute("INSERT INTO faqs(question,answer) VALUES(?,?)",(q,a))

conn.commit()
conn.close()
print(f"Seeded DB at {DB_PATH}")
