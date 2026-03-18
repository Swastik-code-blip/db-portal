#!/usr/bin/env python3
"""
DB Hardware Portal — ONE CLICK SETUP
Run: py SETUP.py
"""
import subprocess, sys, os

# Fix: quote the python path properly for Windows spaces
PY = f'"{sys.executable}"'

def run(cmd):
    print(f"  >> {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode

print("\n" + "="*60)
print("  DB HARDWARE PORTAL — DAINIK BHASKAR")
print("  Auto Setup Script v3.1")
print(f"  Python: {sys.executable}")
print("="*60 + "\n")

# 1. Install deps
print("[1/5] Installing dependencies...")
r = run(f'{PY} -m pip install django openpyxl --quiet')
if r != 0:
    print("  WARNING: pip install had issues. Trying anyway...")

# 2. Migrate
print("\n[2/5] Setting up database...")
r = run(f'{PY} manage.py migrate --run-syncdb')
if r != 0:
    print("  ERROR: Migration failed. Make sure you are running from the db_portal folder.")
    input("Press Enter to exit...")
    sys.exit(1)

# 3. Create superadmin inline
print("\n[3/5] Creating Super Admin account...")
admin_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_create_admin.py")
with open(admin_script, "w") as f:
    f.write("""
import django, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'db_portal.settings'
django.setup()
from hardware.models import CustomUser
if not CustomUser.objects.filter(username='admin').exists():
    u = CustomUser.objects.create_superuser('admin', 'admin@dainikbhaskar.com', 'admin123')
    u.role = 'superadmin'
    u.first_name = 'Super'
    u.last_name = 'Admin'
    u.save()
    print('  Super Admin created: username=admin  password=admin123')
else:
    u = CustomUser.objects.get(username='admin')
    if u.role != 'superadmin':
        u.role = 'superadmin'
        u.save()
    print('  Admin already exists — role confirmed as superadmin')
""")
run(f'{PY} "{admin_script}"')
try:
    os.remove(admin_script)
except:
    pass

# 4. Load sample data
print("\n[4/5] Loading sample data...")
run(f'{PY} load_sample_data.py')

# 5. Launch
print("\n[5/5] Starting server...")
print("\n" + "="*60)
print("  PORTAL IS READY!")
print("  Open in browser: http://127.0.0.1:8000/")
print("  Username: admin")
print("  Password: admin123")
print("  Press CTRL+C to stop the server")
print("="*60 + "\n")
run(f'{PY} manage.py runserver')
