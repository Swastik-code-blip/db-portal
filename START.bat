@echo off
title DB Hardware Portal — Dainik Bhaskar
color 0B
echo.
echo  ============================================================
echo   DB HARDWARE PORTAL — DAINIK BHASKAR v3.1
echo  ============================================================
echo.
echo  Starting setup, please wait...
echo.
py SETUP.py
if errorlevel 1 (
    echo.
    echo  ERROR: py command failed, trying python...
    python SETUP.py
)
pause
