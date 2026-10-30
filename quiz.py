import sqlite3
import random
import time
from pathlib import Path
import infoManager

DEFAULT_IMAGE = (Path(__file__).resolve().parent / "UI" / "Images" / "default-question.png").as_uri()

class ConsoleQuiz:
    def __init__(self):
        self.category = infoManager.getCategory()
        self.db_path = infoManager.get_questions_db_path(self.category)
        self.ended = False
        self.questions = []
        self.index = 0
        self.score = 0
        self.mistakes = 0
        self.max_time = 30 * 60
        self.start_time = time.time()
        self.load_questions()

    def load_questions(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("SELECT qid, text, correct, image, theme_id FROM questions WHERE cat = ?", (self.category,))
        all_qs = cur.fetchall()
        self.questions = random.sample(all_qs, min(30, len(all_qs)))
        con.close()

    def get_current_question_text(self):
        if self.index < len(self.questions):
            return self.questions[self.index][1]
        return ""

    def get_current_answers(self):
        if self.index >= len(self.questions):
            return {}
        qid = self.questions[self.index][0]
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("SELECT option_num, text FROM answers WHERE qid = ?", (qid,))
        answers = {row[0]: row[1] for row in cur.fetchall()}
        con.close()
        return answers

    def get_current_image(self):
        if self.index < len(self.questions):
            image = self.questions[self.index][3]
            return image if image else DEFAULT_IMAGE
        return ""

    def get_timer_text(self):
        elapsed = int(time.time() - self.start_time)
        remaining = max(0, self.max_time - elapsed)
        minutes = remaining // 60
        seconds = remaining % 60
        return f"{minutes}:{seconds:02d}"

    def answer_current_question(self, user_choice):
        if self.index >= len(self.questions):
            return False, "Quiz finished"

        qid, text, correct, image, theme_id = self.questions[self.index]
        answers = self.get_current_answers()
        if user_choice not in answers:
            return False, "Invalid choice"

        if user_choice == correct:
            self.score += 1
            result = True
        else:
            self.mistakes += 1
            self.save_wrong(qid, theme_id)
            result = False

        self.index += 1
        return result, "Correct" if result else "Incorrect"

    def skip_current_question(self):
        if self.index < len(self.questions):
            question = self.questions.pop(self.index)
            self.questions.append(question)
            return True
        return False

    def save_wrong(self, qid, theme_id):
        db = sqlite3.connect(infoManager.get_db_path())
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS wrong_questions (qid TEXT PRIMARY KEY)")
        c.execute("INSERT OR IGNORE INTO wrong_questions (qid) VALUES (?)", (qid,))
        c.execute("CREATE TABLE IF NOT EXISTS failed_themes (theme_id INTEGER PRIMARY KEY, failures INTEGER DEFAULT 0)")
        c.execute("""
            INSERT INTO failed_themes (theme_id, failures) VALUES (?, 1)
            ON CONFLICT(theme_id) DO UPDATE SET failures = failures + 1
        """, (theme_id,))
        db.commit()
        db.close()

    def is_finished(self):
        if self.index >= len(self.questions) or self.mistakes >= 3:
            return True
        if time.time() - self.start_time > self.max_time:
            return True
        return False

    def get_score(self):
        return self.score

    def get_mistakes(self):
        return self.mistakes

    def get_total_questions(self):
        return len(self.questions)

    def end_quiz(self):
        if self.ended:
            return
        self.ended = True

        db = sqlite3.connect(infoManager.get_db_path())
        c = db.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                passed INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                total_score INTEGER DEFAULT 0,
                total_tests INTEGER DEFAULT 0
            )
        """)
        if c.execute("SELECT COUNT(*) FROM stats").fetchone()[0] == 0:
            c.execute("INSERT INTO stats (passed, failed, total_score, total_tests) VALUES (0, 0, 0, 0)")

        time_expired = time.time() - self.start_time > self.max_time
        passed = self.mistakes < 3 and not time_expired

        if passed:
            c.execute("UPDATE stats SET passed = passed + 1")
        else:
            c.execute("UPDATE stats SET failed = failed + 1")

        c.execute("UPDATE stats SET total_score = total_score + ?, total_tests = total_tests + 1", (self.score,))
        db.commit()
        db.close()


class ConsoleSequentialQuiz:
    def __init__(self):
        self.category = infoManager.getCategory()
        self.db_path = infoManager.get_questions_db_path(self.category)
        self.questions = []
        self.index = 0
        self.score = 0
        self.mistakes = 0
        self.load_questions()

    def load_questions(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("SELECT qid, text, correct, image, theme_id FROM questions WHERE cat = ? ORDER BY qid", (self.category,))
        self.questions = cur.fetchall()
        con.close()

    def get_current_question_text(self):
        if self.index < len(self.questions):
            return self.questions[self.index][1]
        return ""

    def get_current_answers(self):
        if self.index >= len(self.questions):
            return {}
        qid = self.questions[self.index][0]
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("SELECT option_num, text FROM answers WHERE qid = ?", (qid,))
        answers = {row[0]: row[1] for row in cur.fetchall()}
        con.close()
        return answers

    def get_current_image(self):
        if self.index < len(self.questions):
            image = self.questions[self.index][3]
            return image if image else DEFAULT_IMAGE
        return DEFAULT_IMAGE

    def get_timer_text(self):
        return "∞"

    def answer_current_question(self, user_choice):
        if self.index >= len(self.questions):
            return False, "Quiz finished"

        qid, text, correct, image, theme_id = self.questions[self.index]
        answers = self.get_current_answers()
        if user_choice not in answers:
            return False, "Invalid choice"

        if user_choice == correct:
            self.score += 1
            result = True
        else:
            self.mistakes += 1
            self.save_wrong(qid, theme_id)
            result = False

        self.index += 1
        return result, "Correct" if result else "Incorrect"

    def skip_current_question(self):
        if self.index < len(self.questions):
            question = self.questions.pop(self.index)
            self.questions.append(question)
            return True
        return False

    def save_wrong(self, qid, theme_id):
        db = sqlite3.connect(infoManager.get_db_path())
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS wrong_questions (qid TEXT PRIMARY KEY)")
        c.execute("INSERT OR IGNORE INTO wrong_questions (qid) VALUES (?)", (qid,))
        c.execute("CREATE TABLE IF NOT EXISTS failed_themes (theme_id INTEGER PRIMARY KEY, failures INTEGER DEFAULT 0)")
        c.execute("""
            INSERT INTO failed_themes (theme_id, failures) VALUES (?, 1)
            ON CONFLICT(theme_id) DO UPDATE SET failures = failures + 1
        """, (theme_id,))
        db.commit()
        db.close()

    def is_finished(self):
        return self.index >= len(self.questions)

    def get_score(self):
        return self.score

    def get_mistakes(self):
        return self.mistakes

    def get_total_questions(self):
        return len(self.questions)

    def end_quiz(self):
        pass



# run the sequential quiz from the terminal
if __name__ == "__main__":
    quiz = ConsoleSequentialQuiz()
    while not quiz.is_finished():
        print(f"\nQ{quiz.index + 1}: {quiz.get_current_question_text()}")
        for num, ans in sorted(quiz.get_current_answers().items()):
            print(f"{num}. {ans}")
        choice = input("Answer (1-4) or s to skip: ").strip().lower()
        if choice == 's':
            quiz.skip_current_question()
            print("Skipped.")
            continue
        try:
            choice_num = int(choice)
            correct, msg = quiz.answer_current_question(choice_num)
            print(msg)
        except:
            print("Invalid input.")
    print(f"Finished! Score: {quiz.get_score()}/{quiz.get_total_questions()}, Mistakes: {quiz.get_mistakes()}")




# run the timed quiz from the terminal
if __name__ == "__main__":
    quiz = ConsoleQuiz()
    while not quiz.is_finished():
        print(f"\nQ{quiz.index + 1}: {quiz.get_current_question_text()}")
        for num, ans in sorted(quiz.get_current_answers().items()):
            print(f"{num}. {ans}")
        print(f"Timer: {quiz.get_timer_text()}")
        choice = input("Answer (1-4) or s to skip: ").strip().lower()
        if choice == 's':
            quiz.skip_current_question()
            print("Skipped.")
            continue
        try:
            choice_num = int(choice)
            correct, msg = quiz.answer_current_question(choice_num)
            print(msg)
        except:
            print("Invalid input.")
    quiz.end_quiz()
    print(f"Finished! Score: {quiz.get_score()}/{quiz.get_total_questions()}, Mistakes: {quiz.get_mistakes()}")
