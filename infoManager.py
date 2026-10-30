import sqlite3
import os
import shutil
from datetime import datetime, date

# keep user data outside the project folder
def get_user_data_dir():
    data_root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    user_data_dir = os.path.join(data_root, "MartvisMowmoba")
    os.makedirs(user_data_dir, exist_ok=True)
    return user_data_dir

def get_db_path():
    return os.path.join(get_user_data_dir(), "info.db")

def get_questions_db_path(category):
    file_name = f"questions_{category}.db"
    user_db_dir = os.path.join(get_user_data_dir(), "DBs")
    os.makedirs(user_db_dir, exist_ok=True)
    user_db_path = os.path.join(user_db_dir, file_name)

    if not os.path.exists(user_db_path):
        app_dir = os.path.dirname(os.path.abspath(__file__))
        bundled_db_path = os.path.join(app_dir, "DBs", file_name)
        if not os.path.isfile(bundled_db_path):
            raise FileNotFoundError(f"Question database was not found: {file_name}")
        shutil.copy2(bundled_db_path, user_db_path)

    return user_db_path

def _connect():
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS info (name TEXT, category TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS dates (id INTEGER PRIMARY KEY AUTOINCREMENT, saved_date TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS wrong_questions (qid TEXT PRIMARY KEY)")
    cur.execute("CREATE TABLE IF NOT EXISTS failed_themes (theme_id INTEGER PRIMARY KEY, failures INTEGER DEFAULT 0)")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            passed INTEGER DEFAULT 0,
            failed INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            total_tests INTEGER DEFAULT 0
        )
    """)
    if cur.execute("SELECT COUNT(*) FROM stats").fetchone()[0] == 0:
        cur.execute("INSERT INTO stats (passed, failed, total_score, total_tests) VALUES (0, 0, 0, 0)")

    con.commit()
    return con

def signin(name, category):
    con = _connect()
    cur = con.cursor()

    cur.execute("DELETE FROM info")
    cur.execute("INSERT OR IGNORE INTO info VALUES (?, ?)", (name, category))

    con.commit()
    con.close()

def getName():
    con = _connect()
    cur = con.cursor()
    cur.execute("SELECT name FROM info")
    result = cur.fetchone()
    con.close()
    return result[0] if result else None

def getCategory():
    con = _connect()
    cur = con.cursor()
    cur.execute("SELECT category FROM info")
    result = cur.fetchone()
    con.close()
    return result[0] if result else None

def info_exists():
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return False
    try:
        con = _connect()
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
    conn = _connect()
    cursor = conn.cursor()

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
    con = _connect()
    cur = con.cursor()
    cur.execute("SELECT passed FROM stats")
    result = cur.fetchone()
    con.close()
    return result[0] if result else None

def getFailed():
    con = _connect()
    cur = con.cursor()
    cur.execute("SELECT failed FROM stats")
    result = cur.fetchone()
    con.close()
    return result[0] if result else None

def getAllTests():
    con = _connect()
    cur = con.cursor()
    cur.execute("SELECT total_tests FROM stats")
    result = cur.fetchone()
    con.close()
    return result[0] if result else None



def get_wrong_questions_html():
    category = getCategory()
    question_db_path = get_questions_db_path(category)

    info_con = _connect()
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

    table_html = (
        '<div class="table-scroll"><table class="wrong-questions-table">'
        '<thead><tr><th class="question-id">QID</th><th>Question</th>'
        '<th>Description</th></tr></thead><tbody>'
    )
    for qid, text, desc in rows:
        table_html += f'<tr><td class="question-id">{qid}</td><td>{text}</td><td>{desc}</td></tr>'
    table_html += "</tbody></table></div>"
    return table_html


def get_most_failed_theme_name():
    category = getCategory()
    info_con = _connect()
    info_cur = info_con.cursor()

    info_cur.execute("SELECT theme_id FROM failed_themes ORDER BY failures DESC LIMIT 1")
    result = info_cur.fetchone()
    info_con.close()

    if not result:
        return "No failed themes recorded."

    theme_id = result[0]

    db_path = get_questions_db_path(category)
    q_con = sqlite3.connect(db_path)
    q_cur = q_con.cursor()
    q_cur.execute("SELECT name FROM themes WHERE id = ?", (theme_id,))
    theme_row = q_cur.fetchone()
    q_con.close()

    if theme_row:
        return theme_row[0]
    else:
        return "Unknown theme"
