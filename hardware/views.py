from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
import json, io
from datetime import datetime, date

from .models import Hardware, Employee, TrashHardware, HardwareProperty, CommandLog, CustomUser, HARDWARE_TYPES, STATUS_CHOICES

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def get_location_filtered_hardware(user, qs=None):
    if qs is None:
        qs = Hardware.objects.select_related('assigned_to')
    if user.has_location_filter:
        qs = qs.filter(location__iexact=user.location)
    return qs

def user_can_access_hw(user, hw):
    if not user.has_location_filter:
        return True
    return hw.location.lower() == user.location.lower()

# ─── DECORATORS ───────────────────────────────────────────────────────────────

def editor_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        if not request.user.can_edit:
            return render(request, 'hardware/403.html', status=403)
        return f(request, *args, **kwargs)
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        if not request.user.can_admin:
            return render(request, 'hardware/403.html', status=403)
        return f(request, *args, **kwargs)
    return wrap

def superadmin_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        if not request.user.is_superadmin_role:
            return render(request, 'hardware/403.html', status=403)
        return f(request, *args, **kwargs)
    return wrap

# ─── AUTH ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', '/'))
        error = 'Invalid credentials. Access denied.'
    return render(request, 'hardware/login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('/login/')

# ─── AUTO FETCH API — called by the script running on any PC ─────────────────

@csrf_exempt
def auto_fetch_api(request):
    """
    POST endpoint called by the auto-fetch script.
    Receives hardware info as JSON and saves it to the portal automatically.
    Auth: username + password in JSON body.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST only'})
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})

    # Authenticate
    username = data.get('username')
    password = data.get('password')
    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({'success': False, 'error': 'Invalid credentials'})
    if not user.can_edit:
        return JsonResponse({'success': False, 'error': 'Insufficient role'})

    hw_data = data.get('hardware', {})
    hw_id = hw_data.get('hw_id', '').strip()
    serial = hw_data.get('serial_number', '').strip()

    if not hw_id or not serial:
        return JsonResponse({'success': False, 'error': 'hw_id and serial_number are required'})

    # Check if already exists
    if Hardware.objects.filter(serial_number=serial).exists():
        hw = Hardware.objects.get(serial_number=serial)
        # Update properties
        hw.properties.all().delete()
        for k, v in hw_data.get('properties', {}).items():
            if k and v:
                HardwareProperty.objects.create(hardware=hw, key=k, value=str(v))
        hw.updated_at = datetime.now()
        hw.save()
        return JsonResponse({'success': True, 'action': 'updated', 'hw_id': hw.hw_id, 'message': f'Hardware {hw.hw_id} updated successfully'})

    # Create new hardware
    try:
        # Handle price
        try:    price = float(hw_data.get('price', 0) or 0)
        except: price = 0

        # Handle purchase date
        pd = hw_data.get('purchase_date', '')
        try:
            pd = datetime.strptime(pd, '%Y-%m-%d').date() if pd else date.today()
        except:
            pd = date.today()

        hw = Hardware.objects.create(
            hw_id=hw_id,
            hardware_type=hw_data.get('hardware_type', 'Desktop'),
            brand=hw_data.get('brand', 'Unknown'),
            model_name=hw_data.get('model_name', 'Unknown'),
            serial_number=serial,
            purchase_date=pd,
            price=price,
            status='active',
            location=hw_data.get('location', ''),
            specifications=hw_data.get('specifications', ''),
            notes=hw_data.get('notes', 'Auto-added via fetch script'),
            created_by=user,
        )
        # Save properties
        for i, (k, v) in enumerate(hw_data.get('properties', {}).items()):
            if k and v:
                HardwareProperty.objects.create(hardware=hw, key=k, value=str(v), order=i)
        return JsonResponse({'success': True, 'action': 'created', 'hw_id': hw.hw_id, 'message': f'Hardware {hw.hw_id} saved to portal successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    hw_qs = get_location_filtered_hardware(request.user)
    total_hw = hw_qs.count()
    active_hw = hw_qs.filter(status='active').count()
    total_emp = Employee.objects.filter(is_active=True).count()
    total_trash = TrashHardware.objects.count()
    hw_by_type = {}
    for t, _ in HARDWARE_TYPES:
        hw_by_type[t] = hw_qs.filter(hardware_type=t).count()
    recent_hw = hw_qs.order_by('-created_at')[:6]
    recent_trash = TrashHardware.objects.order_by('-disposed_date')[:4]
    all_locations = Hardware.objects.values_list('location', flat=True).distinct().exclude(location='').order_by('location')
    context = {
        'total_hw': total_hw, 'total_emp': total_emp,
        'total_trash': total_trash, 'active_hw': active_hw,
        'hw_by_type': hw_by_type, 'recent_hw': recent_hw,
        'recent_trash': recent_trash, 'all_locations': all_locations,
        'user_location': request.user.location,
    }
    return render(request, 'hardware/dashboard.html', context)

# ─── HARDWARE ─────────────────────────────────────────────────────────────────

@login_required
def hardware_list(request):
    hw_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    location_filter = request.GET.get('location', '')
    hardware = get_location_filtered_hardware(request.user)
    if hw_type: hardware = hardware.filter(hardware_type=hw_type)
    if status: hardware = hardware.filter(status=status)
    if location_filter: hardware = hardware.filter(location__icontains=location_filter)
    if search:
        hardware = hardware.filter(
            Q(hw_id__icontains=search)|Q(brand__icontains=search)|
            Q(model_name__icontains=search)|Q(serial_number__icontains=search)|
            Q(location__icontains=search)
        )
    hardware = hardware.order_by('-created_at')
    all_locations = Hardware.objects.values_list('location', flat=True).distinct().exclude(location='').order_by('location')
    return render(request, 'hardware/hardware_list.html', {
        'hardware': hardware, 'hardware_types': HARDWARE_TYPES,
        'status_choices': STATUS_CHOICES, 'selected_type': hw_type,
        'selected_status': status, 'search': search,
        'all_locations': all_locations, 'selected_location': location_filter,
    })

@login_required
def hardware_detail(request, pk):
    hw = get_object_or_404(Hardware, pk=pk)
    if not user_can_access_hw(request.user, hw):
        return render(request, 'hardware/403.html', status=403)
    props = hw.properties.all()
    return render(request, 'hardware/hardware_detail.html', {'hw': hw, 'props': props, 'status_choices': STATUS_CHOICES})

@login_required
def hardware_status_change(request, pk):
    if not request.user.can_edit:
        return JsonResponse({'success': False, 'error': 'Insufficient privileges'})
    if request.method == 'POST':
        hw = get_object_or_404(Hardware, pk=pk)
        if not user_can_access_hw(request.user, hw):
            return JsonResponse({'success': False, 'error': 'Cannot edit hardware outside your location'})
        new_status = request.POST.get('status')
        if new_status not in [s for s,_ in STATUS_CHOICES]:
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        hw.status = new_status
        hw.save()
        return JsonResponse({'success': True, 'status': hw.status})
    return JsonResponse({'success': False})

@editor_required
def hardware_add(request):
    if request.method == 'POST':
        try:
            assigned_to_id = request.POST.get('assigned_to')
            location = request.POST.get('location', '')
            if request.user.has_location_filter:
                location = request.user.location
            hw = Hardware(
                hw_id=request.POST.get('hw_id'),
                hardware_type=request.POST.get('hardware_type'),
                brand=request.POST.get('brand'),
                model_name=request.POST.get('model_name'),
                serial_number=request.POST.get('serial_number'),
                purchase_date=request.POST.get('purchase_date'),
                price=request.POST.get('price') or 0,
                status=request.POST.get('status', 'active'),
                location=location,
                specifications=request.POST.get('specifications', ''),
                notes=request.POST.get('notes', ''),
                created_by=request.user,
            )
            if request.POST.get('warranty_expiry'):
                hw.warranty_expiry = request.POST.get('warranty_expiry')
            if assigned_to_id:
                hw.assigned_to_id = assigned_to_id
            hw.save()
            keys = request.POST.getlist('prop_key[]')
            vals = request.POST.getlist('prop_val[]')
            for i, (k, v) in enumerate(zip(keys, vals)):
                if k.strip() and v.strip():
                    HardwareProperty.objects.create(hardware=hw, key=k.strip(), value=v.strip(), order=i)
            return JsonResponse({'success': True, 'id': hw.pk, 'hw_id': hw.hw_id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    employees = Employee.objects.filter(is_active=True)
    all_locations = Hardware.objects.values_list('location', flat=True).distinct().exclude(location='').order_by('location')
    return render(request, 'hardware/hardware_add.html', {
        'hardware_types': HARDWARE_TYPES, 'status_choices': STATUS_CHOICES,
        'employees': employees, 'all_locations': all_locations,
        'user_location': request.user.location,
    })

@editor_required
def hardware_edit(request, pk):
    hw = get_object_or_404(Hardware, pk=pk)
    if not user_can_access_hw(request.user, hw):
        return render(request, 'hardware/403.html', status=403)
    if request.method == 'POST':
        try:
            hw.hw_id = request.POST.get('hw_id', hw.hw_id)
            hw.hardware_type = request.POST.get('hardware_type', hw.hardware_type)
            hw.brand = request.POST.get('brand', hw.brand)
            hw.model_name = request.POST.get('model_name', hw.model_name)
            hw.serial_number = request.POST.get('serial_number', hw.serial_number)
            hw.purchase_date = request.POST.get('purchase_date', hw.purchase_date)
            hw.price = request.POST.get('price', hw.price)
            hw.status = request.POST.get('status', hw.status)
            hw.specifications = request.POST.get('specifications', hw.specifications)
            hw.notes = request.POST.get('notes', hw.notes)
            if request.user.can_admin:
                hw.location = request.POST.get('location', hw.location)
            assigned_to_id = request.POST.get('assigned_to')
            hw.assigned_to_id = assigned_to_id if assigned_to_id else None
            if request.POST.get('warranty_expiry'):
                hw.warranty_expiry = request.POST.get('warranty_expiry')
            hw.save()
            hw.properties.all().delete()
            keys = request.POST.getlist('prop_key[]')
            vals = request.POST.getlist('prop_val[]')
            for i, (k, v) in enumerate(zip(keys, vals)):
                if k.strip() and v.strip():
                    HardwareProperty.objects.create(hardware=hw, key=k.strip(), value=v.strip(), order=i)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    employees = Employee.objects.filter(is_active=True)
    props = list(hw.properties.values('key', 'value'))
    all_locations = Hardware.objects.values_list('location', flat=True).distinct().exclude(location='').order_by('location')
    return render(request, 'hardware/hardware_edit.html', {
        'hw': hw, 'hardware_types': HARDWARE_TYPES, 'status_choices': STATUS_CHOICES,
        'employees': employees, 'props': props, 'all_locations': all_locations,
    })

# ─── EXCEL ────────────────────────────────────────────────────────────────────

@login_required
def export_hardware_excel(request):
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
    except ImportError:
        return HttpResponse("openpyxl not installed.", status=500)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hardware Inventory"
    headers = ['HW ID','Type','Brand','Model','Serial No','Status','Location','Purchase Date','Warranty Expiry','Price','Assigned To (Emp ID)','Specifications','Notes']
    hf = PatternFill("solid", fgColor="0F1729")
    hfont = Font(bold=True, color="00F5FF", name="Consolas")
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = hf; cell.font = hfont
        cell.alignment = Alignment(horizontal='center')
        ws.column_dimensions[cell.column_letter].width = max(15, len(h)+2)
    for hw in get_location_filtered_hardware(request.user).select_related('assigned_to').all():
        ws.append([hw.hw_id, hw.hardware_type, hw.brand, hw.model_name, hw.serial_number, hw.status, hw.location, str(hw.purchase_date), str(hw.warranty_expiry) if hw.warranty_expiry else '', float(hw.price), hw.assigned_to.emp_id if hw.assigned_to else '', hw.specifications, hw.notes])
    ws2 = wb.create_sheet("Properties")
    ws2.append(['HW ID','Property Key','Property Value'])
    for p in HardwareProperty.objects.select_related('hardware').all():
        ws2.append([p.hardware.hw_id, p.key, p.value])
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    r = HttpResponse(buf.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    r['Content-Disposition'] = f'attachment; filename="DB_Hardware_{date.today()}.xlsx"'
    return r

@editor_required
def import_hardware_excel(request):
    if request.method == 'POST':
        try:
            import openpyxl
        except ImportError:
            return JsonResponse({'success': False, 'error': 'openpyxl not installed'})
        f = request.FILES.get('excel_file')
        if not f:
            return JsonResponse({'success': False, 'error': 'No file uploaded'})
        try:
            wb = openpyxl.load_workbook(f); ws = wb.active
            added = 0; skipped = 0; errors = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row[0]: continue
                hw_id = str(row[0]).strip()
                if Hardware.objects.filter(hw_id=hw_id).exists():
                    skipped += 1; continue
                try:
                    assigned = None
                    if len(row) > 10 and row[10]:
                        try: assigned = Employee.objects.get(emp_id=str(row[10]).strip())
                        except: pass
                    pd = row[7] if len(row)>7 else date.today()
                    if isinstance(pd, str):
                        try: pd = datetime.strptime(pd,'%Y-%m-%d').date()
                        except: pd = date.today()
                    elif hasattr(pd,'date'): pd = pd.date()
                    location = str(row[6] or '').strip() if len(row)>6 else ''
                    if request.user.has_location_filter: location = request.user.location
                    Hardware.objects.create(
                        hw_id=hw_id, hardware_type=str(row[1] or 'Other').strip(),
                        brand=str(row[2] or '').strip(), model_name=str(row[3] or '').strip(),
                        serial_number=str(row[4] or hw_id+'-SN').strip(),
                        status=str(row[5] or 'active').strip(), location=location,
                        purchase_date=pd, price=float(row[9] or 0) if len(row)>9 else 0,
                        assigned_to=assigned,
                        specifications=str(row[11] or '').strip() if len(row)>11 else '',
                        notes=str(row[12] or '').strip() if len(row)>12 else '',
                        created_by=request.user,
                    )
                    added += 1
                except Exception as e:
                    errors.append(f"Row {hw_id}: {str(e)}")
            return JsonResponse({'success': True, 'added': added, 'skipped': skipped, 'errors': errors})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

def export_template_excel(request):
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
    except ImportError:
        return HttpResponse("openpyxl not installed.", status=500)
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Hardware Inventory"
    headers = ['HW ID','Type','Brand','Model','Serial No','Status','Location','Purchase Date','Warranty Expiry','Price','Assigned To (Emp ID)','Specifications','Notes']
    hf = PatternFill("solid", fgColor="0F1729")
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = hf; cell.font = Font(bold=True, color="00F5FF", name="Consolas")
        ws.column_dimensions[cell.column_letter].width = 18
    ws.append(['HW-001','Laptop','Dell','Inspiron 15','SN12345','active','Head Office','2024-01-15','2026-01-15',55000,'EMP-001','Intel i5 8GB RAM',''])
    ws2 = wb.create_sheet("Valid Types")
    ws2.append(['Valid Hardware Types'])
    for t,_ in HARDWARE_TYPES: ws2.append([t])
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    r = HttpResponse(buf.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    r['Content-Disposition'] = 'attachment; filename="DB_Hardware_Import_Template.xlsx"'
    return r

# ─── EMPLOYEES ────────────────────────────────────────────────────────────────

@login_required
def employee_list(request):
    search = request.GET.get('search','')
    employees = Employee.objects.annotate(hw_count=Count('assigned_hardware')).order_by('name')
    if search:
        employees = Employee.objects.filter(Q(emp_id__icontains=search)|Q(name__icontains=search)|Q(department__icontains=search)).annotate(hw_count=Count('assigned_hardware'))
    return render(request,'hardware/employee_list.html',{'employees':employees,'search':search})

@login_required
def employee_detail(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    assigned_hw = get_location_filtered_hardware(request.user).filter(assigned_to=emp).prefetch_related('properties')
    return render(request,'hardware/employee_detail.html',{'emp':emp,'assigned_hw':assigned_hw})

@editor_required
def employee_add(request):
    if request.method == 'POST':
        try:
            emp = Employee.objects.create(
                emp_id=request.POST.get('emp_id'), name=request.POST.get('name'),
                department=request.POST.get('department'), email=request.POST.get('email'),
                phone=request.POST.get('phone',''), designation=request.POST.get('designation'),
            )
            return JsonResponse({'success': True, 'id': emp.pk})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return render(request,'hardware/employee_add.html')

@login_required
def employee_search_api(request):
    q = request.GET.get('q','')
    if not q: return JsonResponse({'results':[]})
    employees = Employee.objects.filter(Q(emp_id__icontains=q)|Q(name__icontains=q))[:10]
    results = []
    for emp in employees:
        hw_qs = get_location_filtered_hardware(request.user).filter(assigned_to=emp).prefetch_related('properties')
        hw_list = [{'hw_id':hw.hw_id,'type':hw.hardware_type,'brand':hw.brand,'model':hw.model_name,'serial':hw.serial_number,'status':hw.status,'specs':hw.specifications,'location':hw.location,'properties':[{'key':p.key,'value':p.value} for p in hw.properties.all()]} for hw in hw_qs]
        results.append({'id':emp.pk,'emp_id':emp.emp_id,'name':emp.name,'department':emp.department,'email':emp.email,'phone':emp.phone,'designation':emp.designation,'hardware':hw_list})
    return JsonResponse({'results':results})

# ─── TRASH ────────────────────────────────────────────────────────────────────

@login_required
def trash_list(request):
    trash = TrashHardware.objects.order_by('-disposed_date')
    return render(request,'hardware/trash_list.html',{'trash':trash,'hardware_types':HARDWARE_TYPES})

@editor_required
def trash_add(request):
    if request.method == 'POST':
        try:
            t = TrashHardware.objects.create(
                hw_id=request.POST.get('hw_id'), hardware_type=request.POST.get('hardware_type'),
                brand=request.POST.get('brand'), model_name=request.POST.get('model_name'),
                serial_number=request.POST.get('serial_number'), reason=request.POST.get('reason'),
                condition=request.POST.get('condition'), original_price=request.POST.get('original_price') or None,
                notes=request.POST.get('notes',''), disposed_by=request.user,
            )
            return JsonResponse({'success': True, 'id': t.pk})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return render(request,'hardware/trash_add.html',{'hardware_types':HARDWARE_TYPES})

# ─── USERS ────────────────────────────────────────────────────────────────────

@admin_required
def user_list(request):
    users = CustomUser.objects.all().order_by('role','username')
    all_locations = Hardware.objects.values_list('location',flat=True).distinct().exclude(location='').order_by('location')
    return render(request,'hardware/user_list.html',{'users':users,'all_locations':all_locations})

@superadmin_required
def user_create(request):
    if request.method == 'POST':
        try:
            user = CustomUser.objects.create_user(
                username=request.POST.get('username'), password=request.POST.get('password'),
                first_name=request.POST.get('first_name',''), last_name=request.POST.get('last_name',''),
                email=request.POST.get('email',''), role=request.POST.get('role','viewer'),
                phone=request.POST.get('phone',''), department=request.POST.get('department',''),
                location=request.POST.get('location',''), created_by=request.user,
            )
            return JsonResponse({'success': True, 'id': user.pk})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    all_locations = Hardware.objects.values_list('location',flat=True).distinct().exclude(location='').order_by('location')
    return render(request,'hardware/user_create.html',{'all_locations':all_locations})

@superadmin_required
def user_toggle(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user: return JsonResponse({'success':False,'error':'Cannot deactivate yourself'})
    user.is_active = not user.is_active; user.save()
    return JsonResponse({'success':True,'active':user.is_active})

@superadmin_required
def user_role_change(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=pk)
        new_role = request.POST.get('role')
        if new_role in ('viewer','editor','admin','superadmin'):
            user.role = new_role; user.save()
            return JsonResponse({'success':True})
    return JsonResponse({'success':False})

@superadmin_required
def user_location_change(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=pk)
        user.location = request.POST.get('location','').strip(); user.save()
        return JsonResponse({'success':True,'location':user.location or 'All Locations'})
    return JsonResponse({'success':False})

# ─── COMMANDS ─────────────────────────────────────────────────────────────────

@login_required
def commands_list(request):
    cmds = CommandLog.objects.all().order_by('platform','title')
    return render(request,'hardware/commands.html',{'cmds':cmds})

@editor_required
def command_add(request):
    if request.method == 'POST':
        try:
            cmd = CommandLog.objects.create(
                title=request.POST.get('title'), description=request.POST.get('description',''),
                platform=request.POST.get('platform','powershell'), command=request.POST.get('command'),
                category=request.POST.get('category',''), created_by=request.user,
            )
            return JsonResponse({'success':True,'id':cmd.pk})
        except Exception as e:
            return JsonResponse({'success':False,'error':str(e)})
    return JsonResponse({'success':False})

@login_required
def command_download(request, pk):
    cmd = get_object_or_404(CommandLog, pk=pk)
    ext = {'python':'py','powershell':'ps1','cmd':'bat'}.get(cmd.platform,'txt')
    ct = {'python':'text/x-python','powershell':'text/plain','cmd':'text/plain'}.get(cmd.platform,'text/plain')
    filename = cmd.title.replace(' ','_').lower() + '.' + ext
    r = HttpResponse(cmd.command, content_type=ct)
    r['Content-Disposition'] = f'attachment; filename="{filename}"'
    return r

# ─── STATS ────────────────────────────────────────────────────────────────────

@login_required
def stats_api(request):
    hw_qs = get_location_filtered_hardware(request.user)
    hw_by_type = {t: hw_qs.filter(hardware_type=t).count() for t,_ in HARDWARE_TYPES}
    return JsonResponse({'hw_by_type':hw_by_type,'total':hw_qs.count(),'active':hw_qs.filter(status='active').count(),'trash':TrashHardware.objects.count(),'employees':Employee.objects.filter(is_active=True).count()})
