@echo off
REM Run with existing venv
setlocal
call .venv\Scripts\activate.bat
python app\main.py
