import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QIcon
import infoManager
from quiz import ConsoleQuiz, ConsoleSequentialQuiz

# paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(BASE_DIR, "UI")
ICON_PATH = os.path.join(PAGES_DIR, "Images", "icon.ico")

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.callback = callback

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if url.scheme() == "pycall":
            if self.callback:
                self.callback(url)
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drivers License App")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setMinimumSize(1500, 1050)

        self.quiz = None
        self.quiz_timer = QTimer()
        self.quiz_timer.timeout.connect(self.update_quiz_ui)

        self.view = QWebEngineView()
        self.view.setPage(CustomWebEnginePage(self.view, self.handle_pycall))
        self.setCentralWidget(self.view)

        self.progresstext = ""

        self.view.urlChanged.connect(self.handle_url)
        if(infoManager.info_exists()):
            self.load_page("home.html")
        else:
            self.load_page("index.html")

        self.test_in_progress = True

    def show_progress(self, cat, pg, _):
        self.progresstext = f"{cat} → gverdi {pg}"
        self.load_page("practice.html")

    def load_page(self, page_name):
        page_path = os.path.join(PAGES_DIR, page_name)
        if not os.path.exists(page_path):
            print(f"! Page not found: {page_name}")
            return

        with open(page_path, "r", encoding="utf-8") as f:
            html = f.read()

        if page_name != "quiz_random.html" and hasattr(self, "quiz") and self.quiz:
            try:
                if hasattr(self.quiz, "timer") and self.quiz.timer.isActive():
                    self.quiz.timer.stop()
                self.quiz_timer.stop()
            except Exception as e:
                print("Error stopping timers:", e)
            self.quiz = None

        # html = html.replace("{{username}}", get_username())

        #if page_name == "practice.html":
           # html = html.replace("{{enabled_style}}", "flex" if self.test_in_progress else "none")
           # html = html.replace("{{disabled_style}}", "none" if self.test_in_progress else "flex")
           # html = html.replace("{{in_progress}}", "Yes" if self.test_in_progress else "No")
           # html = html.replace("{{progress}}", self.progresstext)
        if page_name == "schoolsmap.html":
            import json
            schools = [
                {"name": "Emsi Driving School", "lat": 41.722626582787434, "lon": 44.73030587850845,
                 "phone": "032 205 08 00", "address": "6 Marijani St, Tbilisi", "website": "https://emsi.ge/"},
                {"name": "'Schumacher' driving school", "lat":41.72587313302842,"lon": 44.745554143752756,
                "phone": "597 171 768", "address": "43 Vazha Pshavela Ave, Tbilisi", "website": "https://m.facebook.com/AutoschoolShumachertbilisi/?ref=bookmarks"},
                {"name": "Formula 1", "lat":41.727829899999996, "lon": 44.76496744110245,
                 "phone": "591 055 014", "address": "9 Vazha Pshavela Ave, Tbilisi", "website": "https://www.facebook.com/formula.ge/"},
                {"name": "auto school 'Marte'", "lat":41.72478761027224, "lon":44.74509408468781,
                "phone": "557 24 03 40", "address": "4 Gigo Gabashvili St, Tbilisi", "website": ""},
                {"name": "Driving School", "lat":41.715582998922876, "lon":44.77733658220694,
                "phone": "557 41 11 05", "address": "2/7 Simon Chikovani St, Tbilisi", "website": "https://www.facebook.com/schoolll/"},
                {"name": "Tbilisi Driving School", "lat":41.722295283609185, "lon": 44.71714125686136,
                "phone": "577 41 48 84", "address": "Sandro Euli Street, Tbilisi 1234", "website": "https://sites.google.com/view/martvisskola/home"},
                {"name": "Pitstop Academy (Motorcycles)", "lat":41.729990998294646, "lon":44.78159209999589,
                "phone": "555 00 11 00", "address": "11a Rafael Agladze St, Tbilisi", "website": ""},
                {"name": "Driving School", "lat":41.70933589060507, "lon":44.79631302882781,
                "phone": "598 55 82 07", "address": "18 Kote Marjanishvili St, Tbilisi", "website": ""},
                {"name": "Driving School", "lat":41.719537063000736, "lon":44.77629773029863,
                "phone": "557 41 11 05", "address": "12 Pekini I Dead End, Tbilisi", "website": "https://www.facebook.com/schoolll/"},
                {"name": "ArtDrive", "lat":41.722060298047545, "lon":44.78916143974326,
                "phone": "571 67 67 27", "address": "Tbilisi, Tsereteli street #2 (Dinamo Arena Tbilisi, 0154)", "website": "http://artdrive.ge/"},
                {"name": "Zura Driving School", "lat":41.71678920635037, "lon":44.77976647731109,
                "phone": "", "address": "71a Merab Kostava St, Tbilisi", "website": ""},
                {"name": "AutoSchool Zao", "lat":41.73474679844285, "lon":44.785506817786896,
                "phone": "557 98 30 38", "address": "Tsereteli Avenue 67, 4 Vani Street, Tbilisi", "website": ""},
                {"name": "AutoSchool Drift", "lat":41.69160373251388, "lon":44.869872215334105,
                "phone": "551 11 80 33", "address": "2 Javakheti Business Center Phoenix 5th Floor Room 11/12 Tbilisi, 0182", "website": ""},
                {"name": "Nino's auto school", "lat": 42.260200208731355, "lon": 42.69245154111726,
                 "phone": "555 03 88 55","address": "Ninoshvili 25, Kutaisi 4600", "website": "https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwi5zp7GgaGOAxXYVvEDHSxzPIIQFnoECDkQAQ&url=https%3A%2F%2Fwww.facebook.com%2FDrivingSchoolwithNINO%2F&usg=AOvVaw2RCJKjA2t2X7pUwtEvGPby&opi=89978449"},
                {"name": "Driving School", "lat": 41.64458842702955, "lon": 41.62828309134257,
                 "phone": "593 90 16 14", "address": "9 Selim Khimshiashvili St, Batumi 6010", "website": "http://www.facebook.com/avtoskola.batumi"},
                {"name": "Driving School 'asvs' - Autodrom", "lat": 41.62798861703887, "lon": 41.63988240859401,
                 "phone": "591 25 10 10", "address": "130 M.Varshanidze, Batumi, Kutaisi 4600", "website": ""},
            ]
            html = html.replace("{{school_data}}", json.dumps(schools))
        elif page_name == "home.html":
            name = infoManager.getName()
            html = html.replace("{{username}}", name)
            html = html.replace("{{success_tests}}", str(infoManager.getPassed()))
            html = html.replace("{{tests_taken}}", str(infoManager.getAllTests()))
            if infoManager.save_and_compare_date() != 0:
                html = html.replace("{{last_session}}", str(infoManager.save_and_compare_date()) + " days ago")
            else:
                html = html.replace("{{last_session}}", "No previous session")
        elif page_name == "quiz_random.html":
            if self.quiz is None:
                self.quiz = ConsoleQuiz()
            html = self.render_quiz_html(html)
            self.quiz_timer.start(1000)
        elif page_name == "quiz_sequential.html":
            from quiz import ConsoleSequentialQuiz
            self.quiz = ConsoleSequentialQuiz()
            html = self.render_quiz_html(html)
        elif page_name == "quiz_result.html":
            if hasattr(self, 'last_quiz_result'):
                result = self.last_quiz_result
                html = html.replace("{{score}}", str(result["score"]))
                html = html.replace("{{total}}", str(result["total"]))
                html = html.replace("{{mistakes}}", str(result["mistakes"]))
                html = html.replace("{{result_text}}", "Passed" if result["passed"] else "Failed")
        elif page_name == "mistake_questions.html":
            mistake_questions_questions_table_html = infoManager.get_wrong_questions_html()
            html = html.replace("{{wrong_questions_table}}", mistake_questions_questions_table_html)
        elif page_name == "stats.html":
            failed_theme_name = infoManager.get_most_failed_theme_name()
            html = html.replace("{{focus_theme}}", failed_theme_name)

        self.view.setHtml(html, QUrl.fromLocalFile(page_path))

    def handle_url(self, url):
        scheme = url.scheme()
        path = url.path().lstrip("/")
        if scheme == "pycall":
            self.handle_pycall(url)
            self.view.back()
        elif scheme == "file":
            filename = os.path.basename(path)
            self.load_page(filename)

    def handle_pycall(self, url):
        from urllib.parse import urlparse, parse_qs
        print("CALLED PYTHON:", url.toString())
        action = url.path().lstrip("/")
        query = parse_qs(url.query())

        if action == "submit_name":
            name = query.get("name", [""])[0]
            category = query.get("category", [""])[0]
            infoManager.signin(name, category)
            self.load_page("home.html")
        elif action.startswith("answer_"):
            if not hasattr(self, 'quiz'):
                print("Quiz not initialized yet")
                return

            print(action)
            ans_str = action.split("_")[1]
            if ans_str.isdigit():
                print(ans_str)
                answer_num = int(ans_str)
                if answer_num == 0:
                    self.quiz.skip_current_question()
                else:
                    valid, msg = self.quiz.answer_current_question(answer_num)
                    print(msg)
                self.update_quiz_ui()
        elif action.startswith("update"):
            import scraper
            scraper.scrape_category(infoManager.getCategory(), self.show_progress)

    def render_quiz_html(self, html):
        question = self.quiz.get_current_question_text()
        answers = self.quiz.get_current_answers()
        image = self.quiz.get_current_image()

        ans1 = answers.get(1, "")
        ans2 = answers.get(2, "")
        ans3 = answers.get(3, "")
        ans4 = answers.get(4, "")

        html = html.replace("{{question}}", question)
        html = html.replace("{{answer1}}", ans1)
        html = html.replace("{{answer2}}", ans2)
        html = html.replace("{{answer3}}", ans3)
        html = html.replace("{{answer4}}", ans4)
        html = html.replace("{{questionimage}}", image)

        try:
            max_time = getattr(self.quiz, "max_time", None)
            if max_time is not None:
                import time
                elapsed = int(time.time() - self.quiz.start_time)
                time_left = max(0, max_time - elapsed)
                html = html.replace("{{max_time_seconds}}", str(max_time))
            else:
                html = html.replace("{{max_time_seconds}}", "∞")
        except Exception as e:
            print("Timer placeholder error:", e)
            html = html.replace("{{max_time_seconds}}", "∞")

        return html

    def update_quiz_ui(self):
        if not self.quiz:
            return

        if self.quiz.is_finished():
            self.quiz_timer.stop()
            self.quiz.end_quiz()

            if isinstance(self.quiz, ConsoleSequentialQuiz):
                result_data = {
                    "score": self.quiz.get_score(),
                    "total": self.quiz.get_total_questions(),
                    "mistakes": self.quiz.get_mistakes(),
                    "passed": True
                }
            else:
                result_data = {
                    "score": self.quiz.get_score(),
                    "total": self.quiz.get_total_questions(),
                    "mistakes": self.quiz.get_mistakes(),
                    "passed": self.quiz.get_mistakes() < 3
                }

            self.quiz = None
            self.load_quiz_result(result_data)
            return

        question = self.quiz.get_current_question_text()
        answers = self.quiz.get_current_answers()
        image = self.quiz.get_current_image()
        timer_text = self.quiz.get_timer_text()

        js_code = f"""
            document.querySelector('h2').innerText = {repr(question)};
            document.getElementById('one').innerText = {repr(answers.get(1, ""))};
            document.getElementById('two').innerText = {repr(answers.get(2, ""))};
            document.getElementById('three').innerText = {repr(answers.get(3, ""))};
            document.getElementById('four').innerText = {repr(answers.get(4, ""))};
            document.getElementById('questionimage').src = {repr(image)};
            document.getElementById('timer').innerText = {repr(timer_text)};
        """
        self.view.page().runJavaScript(js_code)

    def load_quiz_result(self, result_data):
        html_path = os.path.join(PAGES_DIR, "quiz_result.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        html = html.replace("{{score}}", str(result_data["score"]))
        html = html.replace("{{total}}", str(result_data["total"]))
        html = html.replace("{{mistakes}}", str(result_data["mistakes"]))
        html = html.replace("{{result_text}}", "Passed" if result_data["passed"] else "Failed")

        self.view.setHtml(html, QUrl.fromLocalFile(html_path))

        def on_load_finished(ok):
            if ok:
                pass
            self.view.loadFinished.disconnect(on_load_finished)

        self.view.loadFinished.connect(on_load_finished)

    def load_quiz_result(self, result_data):
        self.last_quiz_result = result_data
        self.load_page("quiz_result.html")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindowInstance = MainWindow()
    app.setWindowIcon(QIcon(ICON_PATH))
    MainWindowInstance.show()
    sys.exit(app.exec_())
