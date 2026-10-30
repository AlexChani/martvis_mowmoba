@echo off

set "APP_ENV_DIR=%USERPROFILE%\AppData\Local\MartvisMowmoba\build-env"
set "APP_ENV_PYTHON=%APP_ENV_DIR%\Scripts\python.exe"

set "APP_SETUP_PYTHON=python"
if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" set "APP_SETUP_PYTHON=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" set "APP_SETUP_PYTHON=%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe" set "APP_SETUP_PYTHON=%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe"
