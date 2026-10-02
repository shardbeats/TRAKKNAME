@echo off
REM Start: create venv if needed, install deps, launch app
setlocal
where python >nul 2>nul || (echo Python 3.11+ required. & exit /b 1)
if not exist .venv (python -m venv .venv)
call .venv\Scripts\activate.bat
pip install -r requirements.txt
python app\main.py
