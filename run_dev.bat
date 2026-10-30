@echo off
cd /d "%~dp0"
call dev_env.bat

if not exist "%APP_ENV_PYTHON%" (
    call setup_dev.bat
    if errorlevel 1 exit /b 1
)

"%APP_ENV_PYTHON%" UImanager.py
