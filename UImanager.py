import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
# from backend import get_username, run_button_action

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(BASE_DIR, "UI")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt HTML App")
        self.view = QWebEngineView()
        self.setCentralWidget(self.view)
        self.load_page("home.html")
        self.view.urlChanged.connect(self.handle_url)

    def load_page(self, page_name):
        # Load HTML and inject variables
        page_path = os.path.join(PAGES_DIR, page_name)
        if not os.path.exists(page_path):
            print(f"⚠️ Page not found: {page_name}")
            return

        with open(page_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Replace placeholder values
        # html = html.replace("{{username}}", get_username())

        self.view.setHtml(html, QUrl.fromLocalFile(page_path))

    def handle_url(self, url):
        scheme = url.scheme()
        path = url.path().lstrip("/")
        if scheme == "pycall":
            # if path == "run_button_action":
                # run_button_action()
            self.view.back()  # cancel navigation, stay on current page
        elif scheme == "file":
            filename = os.path.basename(path)
            self.load_page(filename)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(1600, 1200)
    window.show()
    app.exec_()
