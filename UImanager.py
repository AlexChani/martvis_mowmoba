import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon

# Paths
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
        self.setWindowIcon(QIcon(ICON_PATH))  # ✅ Taskbar icon
        self.setMinimumSize(1400, 1050)

        self.view = QWebEngineView()
        self.view.setPage(CustomWebEnginePage(self.view, self.handle_pycall))
        self.setCentralWidget(self.view)

        self.view.urlChanged.connect(self.handle_url)
        self.load_page("home.html")

    def load_page(self, page_name):
        page_path = os.path.join(PAGES_DIR, page_name)
        if not os.path.exists(page_path):
            print(f"! Page not found: {page_name}")
            return

        with open(page_path, "r", encoding="utf-8") as f:
            html = f.read()

        # html = html.replace("{{username}}", get_username())

        self.view.setHtml(html, QUrl.fromLocalFile(page_path))

    def handle_url(self, url):
        scheme = url.scheme()
        path = url.path().lstrip("/")
        if scheme == "pycall":
            self.handle_pycall(url)
            self.view.back()  # stay on the same page
        elif scheme == "file":
            filename = os.path.basename(path)
            self.load_page(filename)

    def handle_pycall(self, url):
        action = url.path().lstrip("/")
        if action == "close":
            self.close()
        elif action == "minimize":
            self.showMinimized()
        elif action == "maximize":
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(ICON_PATH))  # ✅ Taskbar icon
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
