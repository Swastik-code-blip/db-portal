@echo off
title DB Portal - Auto Hardware Fetcher
color 0B
echo.
echo ===================================================
echo   DB PORTAL - AUTO HARDWARE FETCHER (CMD)
echo ===================================================
echo.

:: Fetch system info
for /f "tokens=2 delims==" %%a in ('wmic bios get SerialNumber /value 2^>nul') do set SERIAL=%%a
for /f "tokens=2 delims==" %%a in ('wmic cpu get Name /value 2^>nul') do set CPU=%%a
for /f "tokens=2 delims==" %%a in ('wmic computersystem get TotalPhysicalMemory /value 2^>nul') do set RAM=%%a
for /f "tokens=2 delims==" %%a in ('wmic path win32_VideoController get name /value 2^>nul') do set GPU=%%a
for /f "tokens=2 delims==" %%a in ('wmic os get Caption /value 2^>nul') do set OS=%%a
for /f "tokens=2 delims==" %%a in ('wmic logicaldisk where "DeviceID='C:'" get Size /value 2^>nul') do set DISK=%%a

echo   Computer : %COMPUTERNAME%
echo   OS       : %OS%
echo   CPU      : %CPU%
echo   Serial   : %SERIAL%
echo   GPU      : %GPU%
echo.
echo ===================================================
echo.
echo This script requires Python to send data to portal.
echo Running Python auto-fetch script...
echo.

if exist auto_fetch.py (
    py auto_fetch.py
) else (
    echo ERROR: auto_fetch.py not found in same folder!
    echo Please download auto_fetch.py from the portal Commands page.
)

pause
