import os
import sys

# use the project folder for app files
# this still works if the app starts somewhere else like program files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QVBoxLayout,
    QStackedLayout, QLabel, QProgressBar, QMessageBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtCore import QUrl, QTimer, Qt, QStandardPaths, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
import infoManager
from quiz import ConsoleQuiz, ConsoleSequentialQuiz

# app paths
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
        if url.scheme() == "file" and isMainFrame:
            if self.callback:
                self.callback(url)
            return False
        if url.scheme().lower() in ("http", "https") and isMainFrame:
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)


class ScrapeWorker(QObject):
    progress = pyqtSignal(str, int, object)
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, category):
        super().__init__()
        self.category = category

    @pyqtSlot()
    def run(self):
        try:
            import scraper
            scraper.scrape_category(self.category, self.progress.emit)
        except Exception as error:
            self.failed.emit(str(error))
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drivers License App")
        self.setWindowIcon(QIcon(ICON_PATH))
        screen_size = QApplication.primaryScreen().availableGeometry()
        self.setMinimumSize(min(850, screen_size.width()), min(560, screen_size.height()))
        self.resize(min(1180, screen_size.width() - 48), min(780, screen_size.height() - 48))

        self.quiz = None
        self.quiz_timer = QTimer()
        self.quiz_timer.timeout.connect(self.update_quiz_ui)
        self.scrape_thread = None
        self.scrape_worker = None
        self.scrape_active = False
        self.scrape_error = None

        cache_root = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
        if not cache_root:
            cache_root = os.path.join(BASE_DIR, "cache")
        webengine_path = os.path.join(cache_root, "MartvisMowmoba", "QtWebEngine")
        cache_path = os.path.join(webengine_path, "Cache")
        storage_path = os.path.join(webengine_path, "Storage")
        os.makedirs(cache_path, exist_ok=True)
        os.makedirs(storage_path, exist_ok=True)
        self.web_profile = QWebEngineProfile.defaultProfile()
        self.web_profile.setCachePath(cache_path)
        self.web_profile.setPersistentStoragePath(storage_path)

        self.container = QWidget(self)
        self.page_stack = QStackedLayout(self.container)
        self.page_stack.setStackingMode(QStackedLayout.StackAll)
        self.page_stack.setContentsMargins(0, 0, 0, 0)

        self.view = QWebEngineView(self.container)
        page = CustomWebEnginePage(self.view, self.handle_url)
        # allow local pages to load the map tiles and library
        page.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        # identify map tile requests from this app
        page.profile().setHttpUserAgent("MartvisMowmoba/1.0")
        self.view.setPage(page)

        self.progress_overlay = QWidget(self.container)
        self.progress_overlay.setObjectName("refreshOverlay")
        self.progress_overlay.setAttribute(Qt.WA_StyledBackground, True)
        self.progress_overlay.setStyleSheet("""
            #refreshOverlay { background-color: rgba(0, 0, 0, 185); }
            #refreshPanel { background-color: #2b2b2b; border: 1px solid #ffb83b; border-radius: 8px; }
            #refreshTitle { color: #fff; font-size: 18px; font-weight: 600; }
            #refreshDetails { color: rgba(255, 255, 255, 0.78); }
            QProgressBar { height: 16px; border: 1px solid #666; border-radius: 4px; background: #1f1f1f; }
            QProgressBar::chunk { background: #ffb83b; border-radius: 3px; }
        """)
        overlay_layout = QVBoxLayout(self.progress_overlay)
        overlay_layout.setContentsMargins(24, 24, 24, 24)
        overlay_layout.addStretch()

        self.progress_panel = QFrame(self.progress_overlay)
        self.progress_panel.setObjectName("refreshPanel")
        self.progress_panel.setMinimumWidth(320)
        self.progress_panel.setMaximumWidth(420)
        panel_layout = QVBoxLayout(self.progress_panel)
        panel_layout.setContentsMargins(24, 20, 24, 20)
        panel_layout.setSpacing(12)

        self.progress_title = QLabel("Refreshing questions", self.progress_panel)
        self.progress_title.setObjectName("refreshTitle")
        self.progress_details = QLabel("Starting refresh...", self.progress_panel)
        self.progress_details.setObjectName("refreshDetails")
        self.progress_details.setWordWrap(True)
        self.progress_bar = QProgressBar(self.progress_panel)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)

        panel_layout.addWidget(self.progress_title)
        panel_layout.addWidget(self.progress_details)
        panel_layout.addWidget(self.progress_bar)
        overlay_layout.addWidget(self.progress_panel, 0, Qt.AlignCenter)
        overlay_layout.addStretch()

        self.page_stack.addWidget(self.view)
        self.page_stack.addWidget(self.progress_overlay)
        self.progress_overlay.hide()
        self.setCentralWidget(self.container)

        self.progresstext = ""

        if(infoManager.info_exists()):
            self.load_page("home.html")
        else:
            self.load_page("index.html")

        self.test_in_progress = True

    def show_refresh_overlay(self):
        self.page_stack.setCurrentWidget(self.progress_overlay)
        self.progress_overlay.show()
        self.progress_overlay.raise_()

    def hide_refresh_overlay(self):
        self.progress_overlay.hide()
        self.page_stack.setCurrentWidget(self.view)

    def start_scrape(self):
        if self.scrape_active:
            return

        self.scrape_active = True
        self.scrape_error = None
        self.progress_title.setText("Refreshing questions")
        self.progress_details.setText("Connecting to the question source...")
        self.show_refresh_overlay()
        QApplication.processEvents()

        self.scrape_thread = QThread(self)
        self.scrape_worker = ScrapeWorker(infoManager.getCategory())
        self.scrape_worker.moveToThread(self.scrape_thread)
        self.scrape_thread.started.connect(self.scrape_worker.run)
        self.scrape_worker.progress.connect(self.show_progress)
        self.scrape_worker.failed.connect(self.scrape_failed)
        self.scrape_worker.finished.connect(self.scrape_thread.quit)
        self.scrape_worker.finished.connect(self.scrape_worker.deleteLater)
        self.scrape_thread.finished.connect(self.scrape_finished)
        self.scrape_thread.finished.connect(self.scrape_thread.deleteLater)
        self.scrape_thread.start()

    def show_progress(self, cat, pg, _):
        self.progresstext = f"{cat} → page {pg}"
        self.progress_details.setText(self.progresstext)

    def scrape_failed(self, message):
        self.scrape_error = message
        self.progress_details.setText("The refresh could not finish")

    def scrape_finished(self):
        self.scrape_active = False
        self.hide_refresh_overlay()
        self.scrape_worker = None
        self.scrape_thread = None

        if self.scrape_error:
            QMessageBox.warning(self, "Refresh failed", self.scrape_error)

    def closeEvent(self, event):
        if self.scrape_active:
            QMessageBox.information(
                self,
                "Refresh in progress",
                "Wait for the question refresh to finish before closing the app."
            )
            event.ignore()
            return

        if self.quiz is not None:
            answer = QMessageBox.question(
                self,
                "Quiz in progress",
                "A quiz is in progress. Close the app and discard this quiz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if answer != QMessageBox.Yes:
                event.ignore()
                return

        self.quiz_timer.stop()
        event.accept()


    def load_page(self, page_name):
        if self.scrape_active:
            return

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
                 "phone": "555 03 88 55","address": "Ninoshvili 25, Kutaisi 4600", "website": "https://www.facebook.com/DrivingSchoolwithNINO/"},
                {"name": "Driving School", "lat": 41.64458842702955, "lon": 41.62828309134257,
                 "phone": "593 90 16 14", "address": "9 Selim Khimshiashvili St, Batumi 6010", "website": "http://www.facebook.com/avtoskola.batumi"},
                {"name": "Driving School 'asvs' - Autodrom", "lat": 41.62798861703887, "lon": 41.63988240859401,
                 "phone": "591 25 10 10", "address": "130 M.Varshanidze, Batumi, Kutaisi 4600", "website": ""},
            ]
            if "const schools = [];" in html:
                html = html.replace("const schools = [];", f"const schools = {json.dumps(schools)};", 1)
            else:
                print("! School list was not added to the map page")
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
        if self.scrape_active:
            return

        scheme = url.scheme()
        path = url.path().lstrip("/")
        if scheme == "pycall":
            self.handle_pycall(url)
        elif scheme == "file":
            filename = os.path.basename(path)
            self.load_page(filename)

    def handle_pycall(self, url):
        from urllib.parse import parse_qs
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

            ans_str = action.split("_")[1]
            if ans_str.isdigit():
                answer_num = int(ans_str)
                if answer_num == 0:
                    self.quiz.skip_current_question()
                else:
                    self.quiz.answer_current_question(answer_num)
                self.update_quiz_ui()
        elif action.startswith("update"):
            self.start_scrape()

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
            if (window.updateAnswerButtons) window.updateAnswerButtons();
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
    # let qt scale the app on high resolution screens
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setOrganizationName("Martvis")
    app.setApplicationName("MartvisMowmoba")
    MainWindowInstance = MainWindow()
    app.setWindowIcon(QIcon(ICON_PATH))
    MainWindowInstance.show()
    sys.exit(app.exec_())
