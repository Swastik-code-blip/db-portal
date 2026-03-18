@echo off
title DB Portal Manual Setup
color 0B
echo.
echo  ============================================================
echo   DB HARDWARE PORTAL — MANUAL SETUP
echo  ============================================================
echo.

echo [1] Installing Django and openpyxl...
py -m pip install django openpyxl
echo.

echo [2] Running database migrations...
py manage.py migrate
echo.

echo [3] Creating admin user...
py manage.py shell -c "from hardware.models import CustomUser; u=CustomUser.objects.create_superuser('admin','admin@db.com','admin123') if not CustomUser.objects.filter(username='admin').exists() else None; u and setattr(u,'role','superadmin') or None; u and u.save()"
echo.

echo [4] Loading sample data...
py load_sample_data.py
echo.

echo  ============================================================
echo   DONE! Open: http://127.0.0.1:8000/
echo   Login: admin / admin123
echo  ============================================================
echo.

echo [5] Starting server (press CTRL+C to stop)...
py manage.py runserver

pause
