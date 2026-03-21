from django.db import migrations, models

NEW_TYPES = [
    ('Laptop', '💻', 0),
    ('Desktop', '🖥', 1),
    ('Server', '🗄', 2),
    ('TV', '📺', 3),
    ('Printer', '🖨', 4),
    ('Scanner', '📠', 5),
    ('CCTV', '📹', 6),
    ('ILL/BB', '🌐', 7),
    ('Mouse', '🖱', 8),
    ('Keyboard', '⌨', 9),
    ('Switch', '🔀', 10),
    ('Other', '📦', 11),
]

REMOVE_TYPES = ['Camera', 'UPS', 'Router', 'CPU', 'Monitor']

def update_types(apps, schema_editor):
    try:
        HardwareType = apps.get_model('hardware', 'HardwareType')
        HardwareType.objects.filter(name__in=REMOVE_TYPES).update(is_active=False)
        for name, icon, order in NEW_TYPES:
            obj, created = HardwareType.objects.get_or_create(name=name)
            obj.icon = icon
            obj.order = order
            obj.is_active = True
            obj.save()
    except Exception:
        pass

def reverse_types(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('hardware', '0003_alter_customuser_options_alter_customuser_managers_and_more'),
    ]
    operations = [
        migrations.CreateModel(
            name='HardwareType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('icon', models.CharField(default='📦', max_length=10)),
                ('order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['order', 'name']},
        ),
        migrations.RunPython(update_types, reverse_types),
    ]
