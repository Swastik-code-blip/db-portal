"""
DB Portal — Auto Fetch & Save Hardware Info
Run: py auto_fetch.py
Auto detects everything, only asks what it cannot find.
"""
import subprocess, platform, uuid, json, urllib.request, urllib.error, socket
from datetime import date

PORTAL_URL = "https://web-production-d8992.up.railway.app"

def run(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
        if '=' in out:
            lines = [l.split('=',1)[-1].strip() for l in out.splitlines() if '=' in l and l.split('=',1)[-1].strip()]
            return lines[0] if lines else ''
        return out
    except:
        return ''

print("="*55)
print("  DB PORTAL — AUTO HARDWARE FETCHER")
print("  Fetching system info automatically...")
print("="*55)

# Auto fetch
computer_name = platform.node()
os_name       = platform.system() + " " + platform.release()
os_version    = platform.version()
architecture  = platform.machine()
serial        = run('wmic bios get SerialNumber /value')
cpu_name      = run('wmic cpu get Name /value')
cpu_cores     = run('wmic cpu get NumberOfCores /value')
ram_bytes     = run('wmic computersystem get TotalPhysicalMemory /value')
gpu           = run('wmic path win32_VideoController get name /value')
disk_size     = run('wmic logicaldisk where "DeviceID=\'C:\'" get Size /value')
disk_free     = run('wmic logicaldisk where "DeviceID=\'C:\'" get FreeSpace /value')
board         = run('wmic baseboard get Product /value')
bios_ver      = run('wmic bios get SMBIOSBIOSVersion /value')
brand_raw     = run('wmic computersystem get Manufacturer /value')
model_raw     = run('wmic computersystem get Model /value')

# Convert bytes
try:    ram_gb = f"{round(int(ram_bytes)/1073741824, 1)} GB"
except: ram_gb = ram_bytes or 'N/A'
try:    disk_gb = f"{round(int(disk_size)/1073741824, 0):.0f} GB"
except: disk_gb = disk_size or 'N/A'
try:    free_gb = f"{round(int(disk_free)/1073741824, 1)} GB"
except: free_gb = disk_free or 'N/A'

# MAC
try:    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
except: mac = 'N/A'

# IP
try:
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith('127.'): ip = 'N/A'
except: ip = 'N/A'

# Detect type
hw_type = 'Desktop'
try:
    chassis = run('wmic systemenclosure get ChassisTypes /value').replace('[','').replace(']','')
    nums = [int(x) for x in chassis.split(',') if x.strip().isdigit()]
    if any(n in [8,9,10,11,12,14,18,21] for n in nums): hw_type = 'Laptop'
    elif any(n in [17,23] for n in nums): hw_type = 'Server'
except: pass

# Clean brand
brand = brand_raw
if not brand or brand.lower() in ['system manufacturer','to be filled by o.e.m.','']:
    brand = run('wmic baseboard get Manufacturer /value')
if not brand or brand.lower() in ['to be filled by o.e.m.','']:
    brand = 'Assembled'

# Clean model
model = model_raw
if not model or model.lower() in ['system product name','to be filled by o.e.m.','']:
    model = computer_name

# Print detected
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
print("="*55)

# Only ask what cannot be detected
print("\n  PLEASE FILL IN:\n")

username = input("  Portal Username: ").strip()
password = input("  Portal Password: ").strip()

hw_id_suggest = computer_name.replace(' ','-').upper()
hw_id = input(f"  Hardware ID [{hw_id_suggest}] (press Enter): ").strip() or hw_id_suggest

location = ''
while not location:
    location = input("  Location (e.g. Head Office, Bhopal): ").strip()
    if not location: print("  Location is required!")

# Price — always ask
price = input("  Purchase Price in Rs (e.g. 45000) press Enter to skip: ").strip() or '0'

# Purchase date
purchase_date = input(f"  Purchase Date (YYYY-MM-DD) press Enter for today [{date.today()}]: ").strip() or str(date.today())

# Serial — ask if not found
if not serial or serial in ['N/A','To Be Filled By O.E.M.']:
    serial = input("  Serial Number (could not detect, please enter): ").strip() or hw_id+'-SN'

# Confirm type
type_input = input(f"  Hardware Type [{hw_type}] press Enter to keep: ").strip()
if type_input: hw_type = type_input

# Confirm brand
brand_input = input(f"  Brand [{brand}] press Enter to keep: ").strip()
if brand_input: brand = brand_input

print("\n  Sending to portal...")

payload = {
    "username": username,
    "password": password,
    "hardware": {
        "hw_id"        : hw_id,
        "hardware_type": hw_type,
        "brand"        : brand,
        "model_name"   : model,
        "serial_number": serial,
        "location"     : location,
        "price"        : price,
        "purchase_date": purchase_date,
        "specifications": f"{cpu_name}, {ram_gb} RAM, {disk_gb} Storage",
        "notes"        : f"Auto-fetched on {date.today()} from {computer_name}",
        "properties"   : {
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
        print(f"\n  SUCCESS! {result.get('message')}")
        print(f"  Hardware ID : {result.get('hw_id')}")
        print(f"  Action      : {result.get('action','saved').upper()}")
        print(f"\n  View at: {PORTAL_URL}/hardware/")
    else:
        print(f"\n  ERROR: {result.get('error')}")
except urllib.error.URLError as e:
    print(f"\n  CANNOT CONNECT: {e}")
    print(f"  Check portal URL: {PORTAL_URL}")

print("\n" + "="*55)
input("  Press Enter to exit...")
