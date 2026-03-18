# DB HARDWARE PORTAL v3.0 — Dainik Bhaskar
## Cyberpunk Hardware Management System — Full Featured

---

## ONE-CLICK SETUP

### Windows (Recommended):
```
Double-click START.bat
```

### PowerShell:
```powershell
python SETUP.py
```

### Manual:
```bash
pip install django openpyxl
python manage.py migrate
python SETUP.py
```

Then open: **http://127.0.0.1:8000/**

Default login: `admin` / `admin123`

---

## FEATURES

| Feature | Details |
|---------|---------|
| Login System | Secure login with role-based access |
| 4 User Roles | Viewer, Editor, Admin, Super Admin |
| Hardware Types | Laptop, Desktop, CPU, Server, Monitor, Camera, Printer, Scanner, Mouse, Keyboard, UPS, Switch, Router, Other |
| Custom Properties | Add RAM, IP, OS, CPU model, any property dynamically |
| Employee Search | Live search by ID or name — shows all assigned hardware |
| Excel Export | Full inventory export with properties + employees |
| Excel Import | Bulk import hardware from Excel (drag & drop) |
| Import Template | Download filled template with valid values |
| Trash Zone | Log dead/damaged/obsolete hardware |
| Command Center | Save PowerShell, CMD, Python scripts — download as .ps1/.bat/.py |
| Auto-fetch Script | Python script downloads and prints system info |
| User Management | Super Admin creates/disables users, changes roles |
| Django Admin | /admin/ for full database access |

---

## USER ROLES

| Role | Permissions |
|------|------------|
| Viewer | View all data only |
| Editor | Add/edit hardware, employees, trash, commands |
| Admin | Editor + view users panel |
| Super Admin | Full access including create/manage users |

---

## PROJECT STRUCTURE

```
db_portal/
├── SETUP.py              ← ONE-CLICK SETUP & LAUNCHER
├── START.bat             ← Windows double-click starter
├── START.ps1             ← PowerShell starter
├── manage.py
├── requirements.txt      ← django, openpyxl
├── load_sample_data.py
├── db_portal/
│   ├── settings.py
│   └── urls.py
├── hardware/
│   ├── models.py         ← CustomUser, Hardware, Employee, TrashHardware, CommandLog, HardwareProperty
│   ├── views.py          ← All logic including Excel import/export
│   ├── urls.py           ← All routes
│   └── admin.py
└── templates/
    ├── base.html          ← Cyberpunk sidebar UI
    └── hardware/
        ├── login.html
        ├── dashboard.html
        ├── hardware_list.html
        ├── hardware_detail.html
        ├── hardware_add.html     ← With Excel import + custom properties
        ├── hardware_edit.html
        ├── employee_list.html    ← Live search
        ├── employee_detail.html
        ├── employee_add.html
        ├── trash_list.html
        ├── trash_add.html
        ├── commands.html         ← Command center with download
        ├── user_list.html
        ├── user_create.html
        └── 403.html
```

---

## HOSTING ON YOUR OWN SERVER

For hosting (Render, Railway, VPS):
1. Set `DEBUG = False` in settings.py
2. Set `ALLOWED_HOSTS = ['yourdomain.com']`
3. Add `pip install gunicorn whitenoise`
4. Run: `gunicorn db_portal.wsgi`
