@echo off
cd /d "%~dp0"

call dev_env.bat

if not exist "%APP_ENV_PYTHON%" (
    "%APP_SETUP_PYTHON%" -m venv "%APP_ENV_DIR%"
    if errorlevel 1 (
        echo Could not create the Python environment. Install Python and try again.
        exit /b 1
    )
)

"%APP_ENV_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo Setup is ready. Run run_dev.bat to start the app.
