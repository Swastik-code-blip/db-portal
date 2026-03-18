"""
DB Portal — Auto Fetch & Save Hardware Info
Run this on any PC: py auto_fetch.py
It will fetch all hardware info and save it directly to the portal.
"""
import subprocess, platform, uuid, json, urllib.request, urllib.error, socket
from datetime import date

PORTAL_URL = "http://127.0.0.1:8000"  # Change to your portal URL if hosted

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except:
        return ''

def get_val(cmd, key):
    out = run(cmd)
    for line in out.splitlines():
        if '=' in line and key.lower() in line.lower():
            return line.split('=', 1)[-1].strip()
    return out.strip() or 'N/A'

print("="*55)
print("  DB PORTAL — AUTO HARDWARE FETCHER")
print("="*55)

# Fetch all info
computer_name = platform.node()
os_name       = platform.system() + " " + platform.release()
os_version    = platform.version()
processor     = platform.processor()
architecture  = platform.machine()
serial        = get_val('wmic bios get SerialNumber /value', 'serialnumber')
ram_bytes     = get_val('wmic computersystem get TotalPhysicalMemory /value', 'totalphysicalmemory')
ram_gb        = f"{round(int(ram_bytes)/1073741824, 1)} GB" if ram_bytes.isdigit() else ram_bytes
cpu_name      = get_val('wmic cpu get Name /value', 'name')
cpu_cores     = get_val('wmic cpu get NumberOfCores /value', 'numberofcores')
gpu           = get_val('wmic path win32_VideoController get name /value', 'name')
disk_size     = get_val('wmic logicaldisk where DeviceID="C:" get Size /value', 'size')
disk_gb       = f"{round(int(disk_size)/1073741824, 0):.0f} GB" if disk_size.isdigit() else disk_size
disk_free     = get_val('wmic logicaldisk where DeviceID="C:" get FreeSpace /value', 'freespace')
disk_free_gb  = f"{round(int(disk_free)/1073741824, 1)} GB" if disk_free.isdigit() else disk_free
mac           = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
ip            = run('for /f "tokens=2 delims=:" %a in (\'ipconfig ^| findstr /i "IPv4"\') do @echo %a').split('\n')[0].strip() or socket.gethostbyname(socket.gethostname())
motherboard   = get_val('wmic baseboard get Manufacturer,Product /value', 'product')
bios_ver      = get_val('wmic bios get SMBIOSBIOSVersion /value', 'smbiosbiosversion')

print(f"\n  Computer Name : {computer_name}")
print(f"  OS            : {os_name}")
print(f"  CPU           : {cpu_name}")
print(f"  Cores         : {cpu_cores}")
print(f"  RAM           : {ram_gb}")
print(f"  Storage C:    : {disk_gb} (Free: {disk_free_gb})")
print(f"  GPU           : {gpu}")
print(f"  Serial No     : {serial}")
print(f"  MAC Address   : {mac}")
print(f"  IP Address    : {ip}")
print(f"  Motherboard   : {motherboard}")
print(f"  BIOS Version  : {bios_ver}")
print("="*55)

# Ask user for portal details
print("\nENTER PORTAL LOGIN DETAILS:")
username = input("  Username: ").strip()
password = input("  Password: ").strip()
hw_id    = input(f"  Hardware ID (press Enter for '{computer_name}'): ").strip() or computer_name
location = input("  Location (e.g. Head Office): ").strip()
hw_type  = input("  Type (Laptop/Desktop/Server etc.) [Desktop]: ").strip() or "Desktop"
brand    = input("  Brand (e.g. Dell, HP, Assembled): ").strip() or "Unknown"
model    = input(f"  Model (press Enter for '{computer_name}'): ").strip() or computer_name

print("\n  Sending to portal...")

payload = {
    "username": username,
    "password": password,
    "hardware": {
        "hw_id": hw_id,
        "hardware_type": hw_type,
        "brand": brand,
        "model_name": model,
        "serial_number": serial if serial != 'N/A' else hw_id + "-SN",
        "location": location,
        "specifications": f"{cpu_name}, {ram_gb} RAM, {disk_gb} Storage",
        "notes": f"Auto-fetched on {date.today()} from {computer_name}",
        "properties": {
            "Computer Name": computer_name,
            "Operating System": os_name,
            "CPU": cpu_name,
            "CPU Cores": cpu_cores,
            "RAM": ram_gb,
            "Storage (C:)": disk_gb,
            "Free Space (C:)": disk_free_gb,
            "GPU": gpu,
            "Serial Number": serial,
            "MAC Address": mac,
            "IP Address": ip,
            "Motherboard": motherboard,
            "BIOS Version": bios_ver,
            "Architecture": architecture,
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
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode())
    if result.get('success'):
        print(f"\n  SUCCESS! {result.get('message')}")
        print(f"  Hardware ID : {result.get('hw_id')}")
        print(f"  Action      : {result.get('action', 'saved').upper()}")
        print(f"\n  View at: {PORTAL_URL}/hardware/")
    else:
        print(f"\n  ERROR: {result.get('error')}")
except urllib.error.URLError as e:
    print(f"\n  CANNOT CONNECT TO PORTAL: {e}")
    print(f"  Make sure portal is running at {PORTAL_URL}")
    print(f"  If hosted elsewhere, edit PORTAL_URL at top of this file")

print("\n" + "="*55)
input("  Press Enter to exit...")
