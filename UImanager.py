import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
import infoManager

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
        self.setWindowIcon(QIcon(ICON_PATH))  # ✅ Taskbar icon
        self.setMinimumSize(1400, 1050)

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
            html = html.replace("{{last_session}}", infoManager.save_and_compare_date() + " days ago")

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
        #elif action == "toggle_test_state":
            #self.test_in_progress = not self.test_in_progress
            #self.load_page("practice.html")
        elif action.startswith("testtype_"):
            test_type = action.replace("testtype_", "")
            self.start_test(test_type)
            self.load_page("quiz.html")
        elif action.startswith("update"):
            import scraper
            scraper.scrape_category(infoManager.getCategory(), self.show_progress)


#    def toggle_test_state(self):
#        self.test_in_progress = not self.test_in_progress
#        self.load_page("practice.html")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindowInstance = MainWindow()
    app.setWindowIcon(QIcon(ICON_PATH))
    MainWindowInstance.show()
    sys.exit(app.exec_())
