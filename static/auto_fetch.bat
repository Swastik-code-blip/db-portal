@echo off
title DB Portal - Auto Hardware Fetcher
color 0B
echo.
echo ====================================================
echo   DB PORTAL - AUTO HARDWARE FETCHER (CMD)
echo   This will fetch your PC info and save to portal
echo ====================================================
echo.

:: Check Python
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed!
    echo Download from: python.org
    pause
    exit
)

echo Step 1: Downloading latest fetch script from portal...
py -c "import urllib.request; urllib.request.urlretrieve('https://web-production-d8992.up.railway.app/static/auto_fetch.py', '%TEMP%\db_auto_fetch.py'); print('  Downloaded successfully!')"

if not exist "%TEMP%\db_auto_fetch.py" (
    echo.
    echo ERROR: Could not download script!
    echo Please check your internet connection.
    pause
    exit
)

echo Step 2: Running hardware detection...
echo.
py "%TEMP%\db_auto_fetch.py"

:: Cleanup temp file
del "%TEMP%\db_auto_fetch.py" >nul 2>&1

pause
