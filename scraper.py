import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import infoManager

# main url for each category and theme id
BASE_URL = "https://teoria.on.ge/tickets/{}/{}"

# category ids used by the source website
CATEGORY_IDS = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 5,
    "T": 7,
    "Tram": 8,
    "B+C1 Mil": 9,
    "AM": 10
}

# theme names by id
THEMES = {
    1: "მძღოლი, მგზავრი და ქვეითი, ნიშნები, კონვეცია",
    2: "უწესივრობა და მართვის პირობები",
    3: "მაფრთხილებელი ნიშნები",
    4: "პრიორიტეტის ნიშნები",
    5: "ამკრძალავი ნიშნები",
    6: "მიმთითებელი ნიშნები",
    7: "საინფორმაციო-მაჩვენებელი ნიშნები",
    8: "სერვისის ნიშნები",
    9: "დამატებითი ინფორმაციის ნიშნები",
    10: "შუქნიშნის სიგნალები",
    11: "მარეგულირებლის სიგნალები",
    12: "სპეციალური სიგნალის გამოყენება",
    13: "საავარიო შუქური სიგნალიზაცია",
    14: "სანათი ხელსაწყოები, ხმოვანი სიგნალი",
    15: "მოძრაობა, მანევრირება, სავალი ნაწილი",
    16: "გასწრება შემხვედრის გვერდის ავლით",
    17: "მოძრაობის სიჩქარე",
    18: "სამუხრუჭე მანძილი, დისტანცია",
    19: "გაჩერება დგომა",
    20: "გზაჯვარედინის გავლა",
    21: "რკინიგზის გადასასვლელი",
    22: "მოძრაობა ავტომაგისტრალზე",
    23: "საცხოვრებელი ზონა, სამარშრუტოს პრიორიტეტი",
    24: "ბუქსირება",
    25: "სასწავლო სვლა",
    26: "გადაზიდვები, ხალხი, ტვირთი",
    27: "ველოსიპედი, მოპედი და პირუტყვის გადარეკვა",
    28: "საგზაო მონიშვნა",
    29: "სამედიცინო დახმარება",
    30: "მოძრაობის უსაფრთხოება",
    31: "ადმინისტრაციული კანონი",
    32: "ეკო-მართვა"
}


def scrape_category(cat_name, progress_fn=None):
    """
    scrape a category from teoria.on.ge and save it to sqlite

    args:
        cat_name: category name like "b" or "am"
        progress_fn: callback for showing progress in the ui
    """

    # track how long the category takes to download
    start_time = time.time()

    cat_id = CATEGORY_IDS.get(cat_name)
    if not cat_id:
        print(f"X category not found: {cat_name}")
        return

    # keep a separate question database for each category
    db_path = infoManager.get_questions_db_path(cat_name)

    # open the database or create it if needed
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # create the tables on the first run
    cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            cat TEXT,
            qid INTEGER PRIMARY KEY,
            theme_id INTEGER,
            text TEXT,
            correct INTEGER,
            image TEXT,
            desc TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            qid INTEGER,
            option_num INTEGER,
            text TEXT,
            PRIMARY KEY (qid, option_num)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)

    # add the theme names before saving questions
    for tid, tname in THEMES.items():
        cur.execute("INSERT OR IGNORE INTO themes (id, name) VALUES (?, ?)", (tid, tname))

    # download all 32 themes one page at a time
    for theme_id in range(1, 33):
        page = 1
        while True:
            if progress_fn:
                progress_fn(f"{cat_name}/T{theme_id}", page, None)

            print(f"[{cat_name}] scraping theme {theme_id} -> page {page}...")

            res = requests.get(f"{BASE_URL.format(cat_id, theme_id)}?page={page}", timeout=20)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select(".item")

            # no items means this theme is finished
            if not items:
                print(f"X no questions found on theme {theme_id} page {page}. stopping.")
                break

            for item in items:
                try:
                    # read the question id
                    qid_tag = item.select_one(".t-num")
                    qid = int(qid_tag.text.strip().lstrip("#")) if qid_tag else None
                    if not qid:
                        continue

                    # save the image url if there is one
                    img = item.select_one(".t-image img")
                    img_url = img["src"].strip() if img else None

                    # read the question text
                    qtxt_el = item.select_one(".t-question .text-wrap")
                    qtext = qtxt_el.text.strip() if qtxt_el else "?"

                    # save the explanation if there is one
                    desc_el = item.select_one(".desc-box-inner p")
                    desc = desc_el.text.strip() if desc_el else ""

                    # collect the answers and mark the correct one
                    correct = None
                    answers = []
                    for ans in item.select("p.t-answer"):
                        if "ans-empty" in ans.get("class", []):
                            continue
                        opt_cls = next((c for c in ans["class"] if c.startswith("t-answer-")), None)
                        if not opt_cls:
                            continue
                        opt_num = int(opt_cls.split("-")[-1])
                        ans_txt_el = ans.select_one(".t-a-text .text-wrap")
                        ans_text = ans_txt_el.text.strip() if ans_txt_el else "?"
                        if ans.get("data-is-correct-list") == "true":
                            correct = opt_num
                        answers.append((opt_num, ans_text))

                    # add the question without replacing existing data
                    cur.execute("INSERT OR IGNORE INTO questions VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (cat_name, qid, theme_id, qtext, correct, img_url, desc))

                    # add the available answers
                    for num, text in answers:
                        cur.execute("INSERT OR IGNORE INTO answers VALUES (?, ?, ?)", (qid, num, text))

                except Exception as e:
                    print("! error while parsing a question:", e)

            page += 1
            time.sleep(0.15)

    con.commit()
    con.close()
    elapsed = time.time() - start_time
    if progress_fn:
        progress_fn(f"{cat_name}/T{theme_id}", page, None)
    print(f"finished category: {cat_name} in {elapsed:.2f} seconds")
