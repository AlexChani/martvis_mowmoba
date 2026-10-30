@echo off
cd /d "%~dp0"

call setup_dev.bat
if errorlevel 1 exit /b 1
call dev_env.bat

"%APP_ENV_PYTHON%" -m PyInstaller --noconfirm --onedir --windowed --name MartvisMowmoba --icon "%~dp0UI\Images\icon.ico" --add-data "%~dp0UI;UI" --add-data "%~dp0DBs;DBs" --specpath "%APP_ENV_DIR%\pyinstaller-spec" --workpath "%APP_ENV_DIR%\pyinstaller-work" --distpath "%~dp0dist" UImanager.py
if errorlevel 1 exit /b 1

echo Built dist\MartvisMowmoba\MartvisMowmoba.exe
