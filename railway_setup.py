"""
Runs automatically on Railway after deploy.
Creates superadmin if not exists.
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db_portal.settings')
django.setup()

from django.core.management import call_command
call_command('migrate', '--run-syncdb')

from hardware.models import CustomUser
if not CustomUser.objects.filter(username='admin').exists():
    u = CustomUser.objects.create_superuser('admin', 'admin@dainikbhaskar.com', 'admin123')
    u.role = 'superadmin'
    u.is_staff = True
    u.is_superuser = True
    u.save()
    print("Superadmin created: admin / admin123")
else:
    print("Admin already exists")
print("Setup complete!")
