#!/usr/bin/env python
"""Run: py load_commands.py  — adds all 3 auto-fetch scripts to portal"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db_portal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from hardware.models import CommandLog, CustomUser

admin = CustomUser.objects.first()

# Clear old commands
CommandLog.objects.all().delete()
print("Cleared old commands...")

# Read script files
def read_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return "# File not found"

py_script  = read_file('static/auto_fetch.py')
ps_script  = read_file('static/auto_fetch.ps1')
bat_script = read_file('static/auto_fetch.bat')

commands = [
    {
        "title": "Auto Fetch & Save to Portal (Python)",
        "platform": "python",
        "category": "DB Portal",
        "description": "Run on any PC — fetches ALL hardware info (CPU, RAM, GPU, Serial, IP, MAC) and saves automatically to this portal. No copy-paste needed!",
        "command": py_script,
    },
    {
        "title": "Auto Fetch & Save to Portal (PowerShell)",
        "platform": "powershell",
        "category": "DB Portal",
        "description": "Run on any Windows PC using PowerShell — fetches all hardware info and saves directly to portal.",
        "command": ps_script,
    },
    {
        "title": "Auto Fetch & Save to Portal (CMD)",
        "platform": "cmd",
        "category": "DB Portal",
        "description": "Run on any Windows PC using Command Prompt — launches the Python auto-fetch script.",
        "command": bat_script,
    },
]

for c in commands:
    obj = CommandLog.objects.create(**c, created_by=admin)
    print(f"  Added: {obj.title}")

print("\nDone! Visit http://127.0.0.1:8000/commands/")
