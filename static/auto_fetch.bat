@echo off
title DB Portal - Auto Hardware Fetcher
color 0B
echo.
echo ====================================================
echo   DB PORTAL - AUTO HARDWARE FETCHER (CMD)
echo   Fetching system info automatically...
echo ====================================================
echo.

:: Check if Python is installed
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed!
    echo Please install Python from python.org
    pause
    exit
)

:: Check if auto_fetch.py exists in same folder
if exist "%~dp0auto_fetch.py" (
    echo Running Python auto-fetch script...
    py "%~dp0auto_fetch.py"
) else (
    echo auto_fetch.py not found in same folder!
    echo.
    echo Please download auto_fetch.py from portal:
    echo https://web-production-d8992.up.railway.app/commands/
    echo.
    echo Then put both files in the same folder and run again.
    pause
)
