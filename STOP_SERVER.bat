@echo off
title Stop AI Attendance Server
color 0c

echo ================================================================
echo    🛑 STOPPING AI ATTENDANCE SYSTEM SERVER (PORT 8000)
echo ================================================================
echo.

for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Terminating PID: %%a ...
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo 🔴 Server stopped successfully!
echo ================================================================
timeout /t 2 >nul
exit
