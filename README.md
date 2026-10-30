# martvis mowmoba

a windows app for practicing georgian driving test questions, learning road signs, checking progress, and finding driving schools in georgia

## start the app while you are working on it

1. install python if it is not already installed
2. open `setup_dev.bat` once
3. open `run_dev.bat` whenever you want to start the app

the setup file makes a python environment in your local app data folder and installs the packages from `requirements.txt`. it looks for python 3.13, 3.12, or 3.11, then tries `python` from your path. it needs internet the first time to download the packages

`run_dev.bat` starts the app from the python files in this folder. you do not have to rebuild the exe after every code change. restart the app to load python changes. if you change `requirements.txt`, run `setup_dev.bat` again

## make the windows exe

1. open `build_windows.bat`
2. wait for the build to finish
3. find the app at `dist\MartvisMowmoba\MartvisMowmoba.exe`

this is a one-folder app. the exe uses the other files in the `_internal` folder, so share or zip the whole `dist\MartvisMowmoba` folder. do not send only the exe

the icon in `UI\Images\icon.ico` is used for the exe and the app window. `brand-logo.png` is the logo shown inside the pages

make a new build when you want to give people an updated exe. the exe does not update itself when you change the project files

## what the files do

- `UImanager.py` opens the desktop window, shows the html pages, handles page links, runs quizzes, and starts question refreshes in the background
- `infoManager.py` saves the profile and quiz progress and finds the question databases
- `quiz.py` loads questions, checks answers, and records scores and mistakes
- `scraper.py` downloads updated questions and explanations from `teoria.on.ge`
- `UI` contains the app pages, shared responsive styles, images, and the driving school map
- `UI\vendor\leaflet` contains the map library used by the map page
- `DBs` contains the starting question database for each license category
- `requirements.txt` lists the python packages needed to run and build the app
- `dev_env.bat` picks the python version and local build environment used by the other batch files
- `setup_dev.bat` creates that environment and installs packages
- `run_dev.bat` starts the app from source
- `build_windows.bat` makes the windows app folder and exe
- `.gitignore` leaves out local settings, build output, and the saved profile database

## how the parts work together

`UImanager.py` opens a pyqt window and loads the pages from `UI`. when a page needs python to do something, it opens a link that starts with `pycall:`. the window catches that link and sends the action to python

the sign-in page sends the name and category. the quiz pages send answer choices. the refresh button starts `scraper.py` on a background thread, so the window can show progress while questions download

`quiz.py` uses the selected category database. random practice picks up to 30 questions and has a 30 minute timer. sequential practice follows the database order and has no timer. wrong answers, scores, and practice dates are saved by `infoManager.py`

## pages

- `index.html` asks for a name and license category
- `home.html` shows the welcome page and saved progress
- `practice.html` links to the quizzes and road sign information
- `quiz_random.html` and `quiz_sequential.html` show the quiz questions
- `quiz_result.html` shows the result after a quiz
- `stats.html` and `mistake_questions.html` show saved practice history
- `roadsigns.html` and the sign category pages explain road signs and signals
- `schoolsmap.html` shows driving schools across georgia
- many page styles are inside their html file. `responsive.css` holds shared layout fixes for different screen sizes
- the school names, locations, phone numbers, and links are added by `UImanager.py`. the map layout is in `schoolsmap.html`

## saved data

the app keeps personal data outside this project folder

- profile, category, dates, scores, and wrong answers go in `%LOCALAPPDATA%\MartvisMowmoba\info.db`
- a writable copy of each question database goes in `%LOCALAPPDATA%\MartvisMowmoba\DBs`
- the databases in this project's `DBs` folder are the starting copies included with the app

the first time a category is used, its starting database is copied to the local app data folder. refreshes update that copy. deleting the local app data folder removes the saved profile, progress, and updated question copies

## maps and internet

the map uses leaflet with openstreetmap tiles. it does not need an api key, but the map tiles need an internet connection. the leaflet files are included in the project; the map tiles load from the internet

question refresh also needs internet because it reads questions from `teoria.on.ge`. the refresh progress overlay appears while the download is running

## common things

- if `setup_dev.bat` says python is missing, install python and try again
- if the map is blank, check the internet connection
- if an exe under `build` says `python313.dll` is missing, close it and use the exe under `dist` instead
- when sharing the exe, include the whole `dist\MartvisMowmoba` folder
- the finished app is in `dist`. new temporary build files are kept in your local app data folder

