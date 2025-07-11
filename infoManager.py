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



def getPassed():
    db_path = "DBS/info.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT passed FROM stats")
    result = cur.fetchone()
    con.close()
    return result[0] if result else None

def getFailed():
    db_path = "DBS/info.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT failed FROM stats")
    result = cur.fetchone()
    con.close()
    return result[0] if result else None

def getAllTests():
    db_path = "DBS/info.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT total_tests FROM stats")
    result = cur.fetchone()
    con.close()
    return result[0] if result else None



def get_wrong_questions_html():
    category = getCategory()
    question_db_path = f"DBs/questions_{category}.db"

    info_con = sqlite3.connect("DBs/info.db")
    info_cur = info_con.cursor()
    info_cur.execute("SELECT qid FROM wrong_questions")
    qid_list = [row[0] for row in info_cur.fetchall()]
    info_con.close()

    if not qid_list:
        return "<p>No mistakes recorded yet.</p>"

    placeholders = ",".join(["?"] * len(qid_list))
    con = sqlite3.connect(question_db_path)
    cur = con.cursor()
    cur.execute(f"SELECT qid, text, desc FROM questions WHERE qid IN ({placeholders})", qid_list)
    rows = cur.fetchall()
    con.close()

    table_html = "<table><tr><th>QID</th><th>Question</th><th>Description</th></tr>"
    for qid, text, desc in rows:
        table_html += f"<tr><td>{qid}</td><td>{text}</td><td>{desc}</td></tr>"
    table_html += "</table>"
    return table_html


def get_most_failed_theme_name():
    category = getCategory()
    info_con = sqlite3.connect("DBs/info.db")
    info_cur = info_con.cursor()

    info_cur.execute("SELECT theme_id FROM failed_themes ORDER BY failures DESC LIMIT 1")
    result = info_cur.fetchone()
    info_con.close()

    if not result:
        return "No failed themes recorded."

    theme_id = result[0]

    db_path = f"DBs/questions_{category}.db"
    q_con = sqlite3.connect(db_path)
    q_cur = q_con.cursor()
    q_cur.execute("SELECT name FROM themes WHERE id = ?", (theme_id,))
    theme_row = q_cur.fetchone()
    q_con.close()

    if theme_row:
        return theme_row[0]
    else:
        return "Unknown theme"