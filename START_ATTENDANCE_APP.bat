@echo off
title AI Classroom Attendance System - Launcher
color 0b

echo ================================================================
echo    📸 AI CLASSROOM ATTENDANCE SYSTEM - WINDOWS 11 LAUNCHER
echo ================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b
)

echo [2/3] Checking Database and System checks...
python manage.py migrate --noinput >nul 2>&1

echo [3/3] Launching AI Attendance System on http://127.0.0.1:8000/ ...
echo.
echo 🟢 Server is starting! Opening your web browser now...
echo.
echo To STOP the server anytime, close this window or run STOP_SERVER.bat
echo ================================================================

start http://127.0.0.1:8000/
python manage.py runserver 0.0.0.0:8000
pause
