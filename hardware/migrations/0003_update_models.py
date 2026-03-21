from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('hardware', '0002_customuser_location'),
    ]
    operations = [
        # HardwareType
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
        # Update Employee model
        migrations.AddField(model_name='employee', name='first_name', field=models.CharField(max_length=100, default='')),
        migrations.AddField(model_name='employee', name='last_name', field=models.CharField(max_length=100, blank=True, default='')),
        migrations.AddField(model_name='employee', name='joining_date', field=models.DateField(null=True, blank=True)),
        migrations.AddField(model_name='employee', name='location', field=models.CharField(max_length=100, blank=True, default='')),
        migrations.AddField(model_name='employee', name='status', field=models.CharField(max_length=20, default='active',
            choices=[('active','Active'),('resigned','Resigned'),('fired','Fired'),('inactive','Inactive')])),
        migrations.AddField(model_name='employee', name='previous_emp_id', field=models.CharField(max_length=30, blank=True, default='')),
        migrations.AddField(model_name='employee', name='emp_id_changed', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='employee', name='created_at', field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now), preserve_default=False),
        migrations.AddField(model_name='employee', name='updated_at', field=models.DateTimeField(auto_now=True)),
        # ResignationRequest
        migrations.CreateModel(
            name='ResignationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('emp_id', models.CharField(max_length=30)),
                ('employee_name', models.CharField(max_length=200)),
                ('reason', models.TextField()),
                ('resignation_letter', models.TextField()),
                ('last_working_date', models.DateField(null=True, blank=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=20, default='pending',
                    choices=[('pending','Pending'),('approved','Approved'),('declined','Declined')])),
                ('review_note', models.TextField(blank=True)),
                ('location', models.CharField(max_length=100, blank=True)),
                ('reviewed_at', models.DateTimeField(null=True, blank=True)),
                ('reviewed_by', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='reviewed_resignations', to='hardware.customuser')),
            ],
        ),
        # Add price default to Hardware
        migrations.AlterField(model_name='hardware', name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10)),
    ]
