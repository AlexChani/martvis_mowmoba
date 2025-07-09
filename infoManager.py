import sqlite3
import os
from datetime import datetime, date

def signin(name, category):
    os.makedirs("DBS", exist_ok=True)
    db_path = "DBS/info.db"

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS info (
            name TEXT,
            category TEXT
        )
    """)

    cur.execute("DELETE FROM info")
    cur.execute("INSERT OR IGNORE INTO info VALUES (?, ?)", (name, category))

    con.commit()
    con.close()

def getName():
    db_path = "DBS/info.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT name FROM info")
    result = cur.fetchone()
    con.close()
    return result[0] if result else None

def getCategory():
    db_path = "DBS/info.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT category FROM info")
    result = cur.fetchone()
    con.close()
    return result[0] if result else None

def info_exists():
    db_path = "DBS/info.db"
    if not os.path.exists(db_path):
        return False
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='info'")
        if not cur.fetchone():
            return False
        cur.execute("SELECT COUNT(*) FROM info")
        count = cur.fetchone()[0]
        con.close()
        return count > 0
    except:
        return False

def save_and_compare_date():
    os.makedirs("DBS", exist_ok=True)
    db_path = "DBS/info.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            saved_date TEXT
        )
    ''')

    today = date.today().isoformat()

    cursor.execute("SELECT 1 FROM dates WHERE saved_date = ?", (today,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO dates (saved_date) VALUES (?)", (today,))
        conn.commit()

    cursor.execute('''
        SELECT saved_date FROM dates
        WHERE saved_date < ?
        ORDER BY saved_date DESC
        LIMIT 1
    ''', (today,))

    result = cursor.fetchone()
    conn.close()

    if result:
        prev_date = datetime.strptime(result[0], "%Y-%m-%d").date()
        return (date.today() - prev_date).days
    else:
        return "0"