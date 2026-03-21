from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('hardware', '0004_update_hardware_types'),
    ]
    operations = [
        migrations.AddField(
            model_name='trashhardware',
            name='sold_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='trashhardware',
            name='sold_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='trashhardware',
            name='sold_to',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='trashhardware',
            name='sold_notes',
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name='TransferRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('from_location', models.CharField(max_length=100)),
                ('to_location', models.CharField(max_length=100)),
                ('reason', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending','Pending'),('approved','Approved'),('declined','Declined')], default='pending', max_length=20)),
                ('review_note', models.TextField(blank=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_requests', to='hardware.employee')),
                ('requested_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfer_requests_made', to='hardware.customuser')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfer_requests_reviewed', to='hardware.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='HardwareApproval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('emp_id', models.CharField(max_length=30)),
                ('employee_name', models.CharField(max_length=200)),
                ('hw_id_text', models.CharField(blank=True, max_length=30)),
                ('request_type', models.CharField(choices=[('repair','Repair Request'),('replace','Replacement Request'),('new','New Hardware Request')], default='repair', max_length=20)),
                ('issue_description', models.TextField()),
                ('location', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(choices=[('pending','Pending'),('approved','Approved'),('declined','Declined')], default='pending', max_length=20)),
                ('review_note', models.TextField(blank=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('hardware', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_requests', to='hardware.hardware')),
                ('assigned_hardware', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_via_approval', to='hardware.hardware')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hardware_approvals_reviewed', to='hardware.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('priority', models.CharField(choices=[('low','Low'),('medium','Medium'),('high','High'),('urgent','Urgent')], default='medium', max_length=20)),
                ('status', models.CharField(choices=[('open','Open'),('in_progress','In Progress'),('done','Done'),('cancelled','Cancelled')], default='open', max_length=20)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to='hardware.customuser')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tasks', to='hardware.customuser')),
            ],
        ),
    ]
