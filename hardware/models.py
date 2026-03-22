from django.db import models
from django.contrib.auth.models import AbstractUser

ROLE_CHOICES = [
    ('viewer', 'Viewer'),
    ('editor', 'Editor'),
    ('admin', 'Admin'),
    ('superadmin', 'Super Admin'),
]


class HardwareType(models.Model):
    """Dynamic hardware types - superadmin can add/edit/remove"""
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=10, default='📦')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    custom_fields = models.TextField(blank=True, default='', help_text='JSON list of field names for this hardware type')

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('maintenance', 'Maintenance'),
    ('repair', 'Under Repair'),
]


class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True,
        help_text="Leave blank to see ALL locations.")
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def can_edit(self):
        return self.role in ('editor', 'admin', 'superadmin')

    @property
    def can_admin(self):
        return self.role in ('admin', 'superadmin')

    @property
    def is_superadmin_role(self):
        return self.role == 'superadmin'

    @property
    def has_location_filter(self):
        return bool(self.location and self.location.strip())


class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resigned', 'Resigned'),
        ('fired', 'Fired'),
        ('inactive', 'Inactive'),
    ]
    emp_id = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    # Location & org fields
    state = models.CharField(max_length=100, blank=True)
    center_name = models.CharField(max_length=200, blank=True)
    office_type = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    grade = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=100, blank=True)
    user_type = models.CharField(max_length=50, blank=True, help_text="e.g. User, Backup, TBA, Stock")
    location = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    previous_emp_id = models.CharField(max_length=30, blank=True, help_text="If emp_id changed, old id stored here")
    emp_id_changed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self):
        return self.status == 'active'

    def __str__(self):
        return f"{self.emp_id} - {self.name}"


class ResignationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    emp_id = models.CharField(max_length=30)
    employee_name = models.CharField(max_length=200)
    reason = models.TextField()
    resignation_letter = models.TextField()
    last_working_date = models.DateField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_resignations')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Resignation - {self.emp_id} ({self.status})"


class Hardware(models.Model):
    hw_id = models.CharField(max_length=30, unique=True)
    hardware_type = models.CharField(max_length=50)
    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    warranty_expiry = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_hardware')
    location = models.CharField(max_length=100, blank=True)
    specifications = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.hw_id} - {self.hardware_type} ({self.brand} {self.model_name})"


class HardwareProperty(models.Model):
    hardware = models.ForeignKey(Hardware, on_delete=models.CASCADE, related_name='properties')
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=500)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'key']


class TrashHardware(models.Model):
    hw_id = models.CharField(max_length=30, unique=True)
    hardware_type = models.CharField(max_length=50)
    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    reason = models.TextField()
    condition = models.CharField(max_length=100)
    disposed_date = models.DateField(auto_now_add=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    disposed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    sold_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sold_date = models.DateField(null=True, blank=True)
    sold_to = models.CharField(max_length=200, blank=True)
    sold_notes = models.TextField(blank=True)


class CommandLog(models.Model):
    PLATFORM_CHOICES = [
        ('powershell', 'PowerShell'),
        ('cmd', 'Command Prompt'),
        ('python', 'Python Script'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='powershell')
    command = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TransferRequest(models.Model):
    """Employee transfer from one location to another"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='transfer_requests')
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    reason = models.TextField(blank=True)
    requested_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfer_requests_made')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfer_requests_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transfer {self.employee.name}: {self.from_location} → {self.to_location} ({self.status})"


class HardwareApproval(models.Model):
    """Hardware replacement/maintenance request by employee"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    REQUEST_TYPES = [
        ('repair', 'Repair Request'),
        ('replace', 'Replacement Request'),
        ('new', 'New Hardware Request'),
    ]
    emp_id = models.CharField(max_length=30)
    employee_name = models.CharField(max_length=200)
    hardware = models.ForeignKey(Hardware, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_requests')
    hw_id_text = models.CharField(max_length=30, blank=True)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, default='repair')
    issue_description = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_hardware = models.ForeignKey(Hardware, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_via_approval')
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='hardware_approvals_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"HW Approval {self.emp_id} - {self.request_type} ({self.status})"


class Task(models.Model):
    """Tasks for admin/superadmin"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tasks')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    due_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"


class Message(models.Model):
    """In-portal notifications/messages"""
    TYPE_CHOICES = [
        ('resignation', 'Resignation'),
        ('transfer', 'Transfer'),
        ('hw_approval', 'HW Approval'),
        ('task', 'Task'),
        ('general', 'General'),
    ]
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='messages')
    sender_name = models.CharField(max_length=200, blank=True)
    message_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message to {self.recipient.username}: {self.title}"
