from django.db import models
from django.contrib.auth.models import AbstractUser

HARDWARE_TYPES = [
    ('Laptop', 'Laptop'),
    ('Desktop', 'Desktop'),
    ('CPU', 'CPU Unit'),
    ('Server', 'Server'),
    ('Monitor', 'Monitor'),
    ('Camera', 'Camera'),
    ('Printer', 'Printer'),
    ('Scanner', 'Scanner'),
    ('Mouse', 'Mouse'),
    ('Keyboard', 'Keyboard'),
    ('UPS', 'UPS'),
    ('Switch', 'Network Switch'),
    ('Router', 'Router'),
    ('Other', 'Other'),
]

STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('maintenance', 'Maintenance'),
    ('repair', 'Under Repair'),
]

ROLE_CHOICES = [
    ('viewer', 'Viewer'),
    ('editor', 'Editor'),
    ('admin', 'Admin'),
    ('superadmin', 'Super Admin'),
]


class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    # Location restricts what hardware the user can see/edit
    location = models.CharField(max_length=100, blank=True,
        help_text="Leave blank to see ALL locations. Set to restrict to one location.")
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
        """True if user is restricted to a specific location"""
        return bool(self.location and self.location.strip())


class Employee(models.Model):
    emp_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    designation = models.CharField(max_length=100)
    joined_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.emp_id} - {self.name}"


class Hardware(models.Model):
    hw_id = models.CharField(max_length=30, unique=True)
    hardware_type = models.CharField(max_length=50, choices=HARDWARE_TYPES)
    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    warranty_expiry = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
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

    def __str__(self):
        return f"{self.hardware.hw_id}: {self.key}={self.value}"


class TrashHardware(models.Model):
    hw_id = models.CharField(max_length=30, unique=True)
    hardware_type = models.CharField(max_length=50, choices=HARDWARE_TYPES)
    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    reason = models.TextField()
    condition = models.CharField(max_length=100)
    disposed_date = models.DateField(auto_now_add=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    disposed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"TRASH-{self.hw_id} - {self.hardware_type}"


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
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.platform})"
