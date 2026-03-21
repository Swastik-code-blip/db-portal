from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('hardware', '0007_employee_new_fields'),
    ]
    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('sender_name', models.CharField(blank=True, max_length=200)),
                ('message_type', models.CharField(choices=[('resignation','Resignation'),('transfer','Transfer'),('hw_approval','HW Approval'),('task','Task'),('general','General')], default='general', max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('related_id', models.IntegerField(blank=True, null=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='hardware.customuser')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
