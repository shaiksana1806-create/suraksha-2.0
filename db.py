import sqlite3

DB = "cases.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id TEXT PRIMARY KEY,
        user TEXT,
        title TEXT,
        description TEXT,
        location TEXT,
        fraud TEXT,
        jurisdiction TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_case(data):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO cases VALUES (?,?,?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()


def fetch_cases():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM cases")
    rows = c.fetchall()
    conn.close()
    return rows


def get_case(cid):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE case_id=?", (cid,))
    row = c.fetchone()
    conn.close()
    return row
