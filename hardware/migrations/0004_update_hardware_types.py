from django.db import migrations, models, connection

NEW_TYPES = [
    ('Laptop', '💻', 0), ('Desktop', '🖥', 1), ('Server', '🗄', 2),
    ('TV', '📺', 3), ('Printer', '🖨', 4), ('Scanner', '📠', 5),
    ('CCTV', '📹', 6), ('ILL/BB', '🌐', 7), ('Mouse', '🖱', 8),
    ('Keyboard', '⌨', 9), ('Switch', '🔀', 10), ('Other', '📦', 11),
]
REMOVE_TYPES = ['Camera', 'UPS', 'Router', 'CPU', 'Monitor']

def create_and_populate(apps, schema_editor):
    # Create table only if it doesn't exist
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hardware_hardwaretype (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL UNIQUE,
                icon VARCHAR(10) NOT NULL DEFAULT '📦',
                "order" INTEGER NOT NULL DEFAULT 0,
                is_active BOOL NOT NULL DEFAULT 1
            )
        """)
    try:
        HardwareType = apps.get_model('hardware', 'HardwareType')
        HardwareType.objects.filter(name__in=REMOVE_TYPES).update(is_active=False)
        for name, icon, order in NEW_TYPES:
            obj, _ = HardwareType.objects.get_or_create(name=name)
            obj.icon = icon; obj.order = order; obj.is_active = True; obj.save()
    except Exception:
        pass

def reverse_fn(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('hardware', '0003_update_models'),
    ]
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(create_and_populate, reverse_fn),
            ],
            state_operations=[
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
            ],
        ),
    ]
