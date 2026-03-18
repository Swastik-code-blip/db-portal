#!/usr/bin/env python
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db_portal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from hardware.models import Employee, Hardware, HardwareProperty, TrashHardware, CommandLog, CustomUser
from datetime import date

print("Loading sample data...")

emp_data = [
    {"emp_id":"EMP-001","name":"Rahul Sharma","department":"IT","email":"rahul@db.com","phone":"+91 98765 43210","designation":"IT Manager"},
    {"emp_id":"EMP-002","name":"Priya Patel","department":"Editorial","email":"priya@db.com","phone":"+91 98765 43211","designation":"Senior Reporter"},
    {"emp_id":"EMP-003","name":"Amit Verma","department":"Design","email":"amit@db.com","phone":"+91 98765 43212","designation":"Graphic Designer"},
    {"emp_id":"EMP-004","name":"Sunita Gupta","department":"Admin","email":"sunita@db.com","phone":"+91 98765 43213","designation":"Admin Officer"},
    {"emp_id":"EMP-005","name":"Vikram Singh","department":"IT","email":"vikram@db.com","phone":"+91 98765 43214","designation":"Network Engineer"},
]
emp_objs = {}
for e in emp_data:
    obj, created = Employee.objects.get_or_create(emp_id=e["emp_id"], defaults=e)
    emp_objs[e["emp_id"]] = obj
    if created: print(f"  Employee: {obj.name}")

hw_data = [
    {"hw_id":"HW-001","hardware_type":"Laptop","brand":"Dell","model_name":"Inspiron 15 3520","serial_number":"DL-SN-001","purchase_date":date(2023,1,15),"warranty_expiry":date(2025,1,15),"price":55000,"status":"active","emp_id":"EMP-001","location":"IT Room","specifications":"Intel i5-12th Gen, 8GB RAM, 512GB SSD","props":[("RAM","8GB DDR4"),("CPU","Intel Core i5-1235U"),("Storage","512GB NVMe SSD"),("OS","Windows 11 Pro"),("Display","15.6 inch FHD")]},
    {"hw_id":"HW-002","hardware_type":"Laptop","brand":"HP","model_name":"EliteBook 840 G9","serial_number":"HP-SN-002","purchase_date":date(2023,3,10),"warranty_expiry":date(2026,3,10),"price":72000,"status":"active","emp_id":"EMP-002","location":"Editorial Floor","specifications":"Intel i7, 16GB RAM, 1TB SSD","props":[("RAM","16GB DDR5"),("CPU","Intel Core i7-1255U"),("Storage","1TB NVMe SSD"),("OS","Windows 11 Pro"),("Battery","56Whr")]},
    {"hw_id":"HW-003","hardware_type":"Desktop","brand":"HP","model_name":"EliteDesk 800 G9","serial_number":"HP-SN-003","purchase_date":date(2022,6,5),"price":48000,"status":"active","emp_id":"EMP-004","location":"Admin Block","specifications":"Intel i5, 8GB RAM, 256GB SSD","props":[("RAM","8GB DDR4"),("CPU","Intel Core i5-12500"),("Storage","256GB SSD + 1TB HDD"),("OS","Windows 11 Pro"),("Form Factor","Small Form Factor")]},
    {"hw_id":"HW-004","hardware_type":"Server","brand":"Dell","model_name":"PowerEdge R740","serial_number":"DL-SN-004","purchase_date":date(2021,9,15),"price":350000,"status":"active","emp_id":"EMP-005","location":"Server Room B2","specifications":"Dual Xeon, 64GB RAM, 4TB RAID","props":[("CPU","Dual Intel Xeon Silver 4210"),("RAM","64GB ECC DDR4"),("Storage","4TB RAID-5"),("OS","Ubuntu Server 22.04"),("IP Address","192.168.1.10"),("Rack Unit","2U")]},
    {"hw_id":"HW-005","hardware_type":"Monitor","brand":"LG","model_name":"27UK850-W","serial_number":"LG-SN-005","purchase_date":date(2022,8,20),"price":28000,"status":"active","emp_id":"EMP-003","location":"Design Studio","specifications":"27 inch 4K UHD IPS","props":[("Resolution","3840x2160 4K UHD"),("Panel","IPS"),("Refresh Rate","60Hz"),("Ports","HDMI, DisplayPort, USB-C")]},
    {"hw_id":"HW-006","hardware_type":"Camera","brand":"Canon","model_name":"EOS 200D Mark II","serial_number":"CN-SN-006","purchase_date":date(2022,4,12),"price":45000,"status":"active","emp_id":"EMP-002","location":"Photo Desk","specifications":"24.1MP DSLR with 18-55mm lens","props":[("Megapixels","24.1 MP"),("Sensor","APS-C CMOS"),("Lens","18-55mm Kit Lens"),("Video","Full HD 1080p")]},
    {"hw_id":"HW-007","hardware_type":"Printer","brand":"HP","model_name":"LaserJet Pro M404dn","serial_number":"HP-SN-007","purchase_date":date(2023,2,1),"price":18000,"status":"active","emp_id":None,"location":"Print Room","specifications":"A4 Mono Laser, 38ppm","props":[("Type","Mono Laser"),("Speed","38 ppm"),("Connectivity","USB, Network"),("Duty Cycle","80,000 pages/month")]},
    {"hw_id":"HW-008","hardware_type":"CPU","brand":"Assembled","model_name":"Workstation WS-IT-01","serial_number":"WS-SN-008","purchase_date":date(2022,11,10),"price":38000,"status":"active","emp_id":"EMP-001","location":"IT Room","specifications":"Ryzen 5 5600X, 16GB RAM","props":[("CPU","AMD Ryzen 5 5600X"),("RAM","16GB DDR4 3200MHz"),("Storage","512GB SSD + 2TB HDD"),("GPU","Integrated"),("OS","Windows 10 Pro")]},
    {"hw_id":"HW-009","hardware_type":"Scanner","brand":"Epson","model_name":"Perfection V39","serial_number":"EP-SN-009","purchase_date":date(2022,4,12),"price":8500,"status":"maintenance","emp_id":None,"location":"Admin Block","specifications":"Flatbed 4800 DPI USB"},
    {"hw_id":"HW-010","hardware_type":"UPS","brand":"APC","model_name":"Back-UPS 1500VA","serial_number":"APC-SN-010","purchase_date":date(2021,5,1),"price":12000,"status":"active","emp_id":None,"location":"Server Room B2","specifications":"1500VA 865W, 8 outlets","props":[("Capacity","1500VA / 865W"),("Runtime","25 min at 50% load"),("Outlets","8 x C13")]},
]

for h in hw_data:
    emp_id = h.pop("emp_id", None)
    props = h.pop("props", [])
    assigned = emp_objs.get(emp_id) if emp_id else None
    obj, created = Hardware.objects.get_or_create(hw_id=h["hw_id"], defaults={**h, "assigned_to": assigned})
    if created:
        print(f"  Hardware: {obj.hw_id} — {obj.brand} {obj.model_name}")
        for i, (k, v) in enumerate(props):
            HardwareProperty.objects.create(hardware=obj, key=k, value=v, order=i)

trash_data = [
    {"hw_id":"TRASH-001","hardware_type":"Laptop","brand":"Lenovo","model_name":"ThinkPad T440","serial_number":"LN-OLD-001","reason":"Hard drive failure — repair cost exceeds unit value","condition":"Dead","original_price":42000,"notes":"Used for 6 years, battery also dead"},
    {"hw_id":"TRASH-002","hardware_type":"Monitor","brand":"Samsung","model_name":"SyncMaster 793S","serial_number":"SM-OLD-002","reason":"CRT monitor — completely obsolete, no VGA ports on new systems","condition":"Obsolete","original_price":8000,"notes":"15-year old CRT"},
    {"hw_id":"TRASH-003","hardware_type":"Printer","brand":"Epson","model_name":"LQ-300+","serial_number":"EP-OLD-003","reason":"Dot matrix — ribbon unavailable, replaced by LaserJet","condition":"Obsolete","original_price":12000},
    {"hw_id":"TRASH-004","hardware_type":"CPU","brand":"Assembled","model_name":"P4 Desktop","serial_number":"P4-OLD-004","reason":"Pentium 4 era — cannot run modern software","condition":"Obsolete","original_price":18000,"notes":"10+ year old system"},
]
for t in trash_data:
    obj, created = TrashHardware.objects.get_or_create(hw_id=t["hw_id"], defaults=t)
    if created: print(f"  Trash: {obj.hw_id}")

cmd_data = [
    {"title":"Get Full System Info","description":"Fetches complete hardware and OS information","platform":"powershell","category":"System","command":"Get-ComputerInfo | Select-Object CsName, OsName, OsVersion, CsProcessors, CsTotalPhysicalMemory, OsArchitecture | Format-List"},
    {"title":"List All Installed Software","description":"Gets all installed programs with version numbers","platform":"powershell","category":"Software","command":"Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | Sort-Object DisplayName | Format-Table -AutoSize"},
    {"title":"Get RAM Details","description":"Shows RAM slots, capacity and speed","platform":"powershell","category":"Hardware","command":"Get-WmiObject -Class Win32_PhysicalMemory | Select-Object BankLabel, Capacity, Speed, Manufacturer | Format-Table -AutoSize"},
    {"title":"Get Disk Info","description":"Shows all drives with size and free space","platform":"powershell","category":"Storage","command":"Get-WmiObject Win32_LogicalDisk | Select-Object DeviceID, @{N='Size(GB)';E={[math]::Round($_.Size/1GB,2)}}, @{N='Free(GB)';E={[math]::Round($_.FreeSpace/1GB,2)}}, @{N='Used%';E={[math]::Round((($_.Size-$_.FreeSpace)/$_.Size)*100,1)}} | Format-Table"},
    {"title":"Get Network Adapters & IP","description":"Lists all network adapters with IP addresses","platform":"powershell","category":"Network","command":"Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | ForEach-Object { $ip = (Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue).IPAddress; Write-Output \"$($_.Name) | MAC: $($_.MacAddress) | IP: $ip\" }"},
    {"title":"Get Serial Number","description":"Gets the hardware serial number of the machine","platform":"powershell","category":"Hardware","command":"(Get-WmiObject -Class Win32_BIOS).SerialNumber"},
    {"title":"Get CPU Details","description":"Shows processor name, cores and speed","platform":"powershell","category":"Hardware","command":"Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed | Format-List"},
    {"title":"Auto Fetch System Info (DB Portal)","description":"Fetches system info and prints it ready to paste into DB Portal","platform":"python","category":"DB Portal","command":"""import subprocess, json, platform, uuid

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except:
        return 'N/A'

info = {
    'Computer Name': platform.node(),
    'OS': platform.system() + ' ' + platform.release(),
    'OS Version': platform.version(),
    'Architecture': platform.machine(),
    'Processor': platform.processor(),
    'Serial Number': run('wmic bios get SerialNumber /value').split('=')[-1] if platform.system()=='Windows' else run('sudo dmidecode -s system-serial-number'),
    'MAC Address': ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1]),
    'RAM': run('wmic computersystem get TotalPhysicalMemory /value').split('=')[-1] if platform.system()=='Windows' else run('grep MemTotal /proc/meminfo'),
}

print('\\n' + '='*50)
print('DB PORTAL — SYSTEM INFO FETCH')
print('='*50)
for k, v in info.items():
    print(f'{k:<20}: {v}')
print('='*50)
print('Copy the values above into the hardware properties!')
"""},
]

superadmin = CustomUser.objects.filter(username='admin').first()
for c in cmd_data:
    obj, created = CommandLog.objects.get_or_create(title=c["title"], defaults={**c, "created_by": superadmin})
    if created: print(f"  Command: {obj.title}")

print("\nSample data loaded!")
print("Open: http://127.0.0.1:8000/")
print("Login: admin / admin123")
