"""
DB Portal — Auto Fetch & Save Hardware Info
Run: py auto_fetch.py
Automatically fetches everything it can, only asks what it cannot detect.
"""
import subprocess, platform, uuid, json, urllib.request, urllib.error, socket, os
from datetime import date

PORTAL_URL = "https://web-production-d8992.up.railway.app"

def run(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
        # Clean up wmic output - get value after =
        if '=' in out:
            lines = [l.split('=',1)[-1].strip() for l in out.splitlines() if '=' in l and l.split('=',1)[-1].strip()]
            return lines[0] if lines else ''
        return out
    except:
        return ''

def ask(prompt, default=''):
    """Only ask if default is empty"""
    if default and default != 'N/A' and default.strip():
        print(f"  {prompt}: {default} (auto-detected)")
        return default
    val = input(f"  {prompt}: ").strip()
    return val or default

print("="*55)
print("  DB PORTAL — AUTO HARDWARE FETCHER")
print("  Fetching system info automatically...")
print("="*55)

# ── AUTO FETCH EVERYTHING ──────────────────────────────
computer_name = platform.node()
os_name       = platform.system() + " " + platform.release()
os_version    = platform.version()
architecture  = platform.machine()
processor     = platform.processor()

serial     = run('wmic bios get SerialNumber /value')
cpu_name   = run('wmic cpu get Name /value')
cpu_cores  = run('wmic cpu get NumberOfCores /value')
ram_bytes  = run('wmic computersystem get TotalPhysicalMemory /value')
gpu        = run('wmic path win32_VideoController get name /value')
disk_size  = run('wmic logicaldisk where "DeviceID=\'C:\'" get Size /value')
disk_free  = run('wmic logicaldisk where "DeviceID=\'C:\'" get FreeSpace /value')
board      = run('wmic baseboard get Product /value')
bios_ver   = run('wmic bios get SMBIOSBIOSVersion /value')

# Convert bytes to readable
try:    ram_gb = f"{round(int(ram_bytes)/1073741824, 1)} GB"
except: ram_gb = ram_bytes or 'N/A'
try:    disk_gb = f"{round(int(disk_size)/1073741824, 0):.0f} GB"
except: disk_gb = disk_size or 'N/A'
try:    free_gb = f"{round(int(disk_free)/1073741824, 1)} GB"
except: free_gb = disk_free or 'N/A'

# MAC address
try:
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
except:
    mac = 'N/A'

# IP address
try:
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith('127.'):
        ip = run('for /f "tokens=2 delims=:" %a in (\'ipconfig ^| findstr /i "IPv4"\') do @echo %a').split('\n')[0].strip()
except:
    ip = 'N/A'

# Detect hardware type
hw_type = 'Desktop'
try:
    chassis = run('wmic systemenclosure get ChassisTypes /value')
    if chassis:
        nums = [int(x) for x in chassis.replace('[','').replace(']','').split(',') if x.strip().isdigit()]
        if any(n in [8,9,10,11,12,14,18,21] for n in nums):
            hw_type = 'Laptop'
        elif any(n in [17,23] for n in nums):
            hw_type = 'Server'
except:
    pass

# Detect brand
brand = run('wmic computersystem get Manufacturer /value')
if not brand or brand.lower() in ['', 'system manufacturer', 'to be filled by o.e.m.']:
    brand = run('wmic baseboard get Manufacturer /value')
if not brand or brand.lower() in ['', 'to be filled by o.e.m.']:
    brand = 'Assembled'

# Detect model
model = run('wmic computersystem get Model /value')
if not model or model.lower() in ['', 'system product name', 'to be filled by o.e.m.']:
    model = computer_name

# Print what was found
print(f"\n  AUTO-DETECTED:")
print(f"  Computer Name : {computer_name}")
print(f"  Hardware Type : {hw_type}")
print(f"  Brand         : {brand}")
print(f"  Model         : {model}")
print(f"  OS            : {os_name}")
print(f"  CPU           : {cpu_name or 'N/A'}")
print(f"  CPU Cores     : {cpu_cores or 'N/A'}")
print(f"  RAM           : {ram_gb}")
print(f"  Storage C:    : {disk_gb} (Free: {free_gb})")
print(f"  GPU           : {gpu or 'N/A'}")
print(f"  Serial No     : {serial or 'NOT FOUND'}")
print(f"  MAC Address   : {mac}")
print(f"  IP Address    : {ip}")
print(f"  Motherboard   : {board or 'N/A'}")
print("="*55)

# ── ONLY ASK WHAT CANNOT BE AUTO-DETECTED ─────────────
print("\n  PLEASE FILL IN (press Enter to use auto-detected value):\n")

username = input("  Portal Username: ").strip()
password = input("  Portal Password: ").strip()

# Hardware ID — suggest computer name
hw_id_suggest = computer_name.replace(' ', '-').upper()
hw_id = input(f"  Hardware ID [{hw_id_suggest}]: ").strip() or hw_id_suggest

# Location — cannot be auto-detected
location = input("  Location (e.g. Head Office, Bhopal): ").strip()
while not location:
    location = input("  Location is required — enter location: ").strip()

# Serial — if not found, ask
if not serial or serial == 'N/A':
    serial = input("  Serial Number (could not auto-detect, please enter): ").strip() or hw_id + "-SN"

# Confirm type and brand (show detected, allow override)
print(f"\n  Hardware Type detected as: {hw_type}")
hw_type_input = input(f"  Press Enter to keep or type (Laptop/Desktop/CPU/Server/Other): ").strip()
if hw_type_input:
    hw_type = hw_type_input

print(f"  Brand detected as: {brand}")
brand_input = input(f"  Press Enter to keep or type correct brand: ").strip()
if brand_input:
    brand = brand_input

# ── SEND TO PORTAL ─────────────────────────────────────
print("\n  Sending to portal...")

payload = {
    "username": username,
    "password": password,
    "hardware": {
        "hw_id": hw_id,
        "hardware_type": hw_type,
        "brand": brand,
        "model_name": model,
        "serial_number": serial,
        "location": location,
        "specifications": f"{cpu_name}, {ram_gb} RAM, {disk_gb} Storage",
        "notes": f"Auto-fetched on {date.today()} from {computer_name}",
        "properties": {
            "Computer Name"   : computer_name,
            "Operating System": os_name,
            "OS Version"      : os_version,
            "CPU"             : cpu_name or 'N/A',
            "CPU Cores"       : cpu_cores or 'N/A',
            "RAM"             : ram_gb,
            "Storage (C:)"    : disk_gb,
            "Free Space (C:)" : free_gb,
            "GPU"             : gpu or 'N/A',
            "Serial Number"   : serial,
            "MAC Address"     : mac,
            "IP Address"      : ip,
            "Motherboard"     : board or 'N/A',
            "BIOS Version"    : bios_ver or 'N/A',
            "Architecture"    : architecture,
        }
    }
}

try:
    req = urllib.request.Request(
        f"{PORTAL_URL}/api/auto-fetch/",
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode())

    if result.get('success'):
        print(f"\n  ✓ SUCCESS! {result.get('message')}")
        print(f"  Hardware ID : {result.get('hw_id')}")
        print(f"  Action      : {result.get('action','saved').upper()}")
        print(f"\n  View at: {PORTAL_URL}/hardware/")
    else:
        print(f"\n  ✗ ERROR: {result.get('error')}")

except urllib.error.URLError as e:
    print(f"\n  ✗ CANNOT CONNECT: {e}")
    print(f"  Make sure portal is running at {PORTAL_URL}")

print("\n" + "="*55)
input("  Press Enter to exit...")
