from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('hardware', '0006_transfer_hw_approval_task'),
    ]
    operations = [
        migrations.AddField(model_name='employee', name='state', field=models.CharField(blank=True, max_length=100, default='')),
        migrations.AddField(model_name='employee', name='center_name', field=models.CharField(blank=True, max_length=200, default='')),
        migrations.AddField(model_name='employee', name='office_type', field=models.CharField(blank=True, max_length=100, default='')),
        migrations.AddField(model_name='employee', name='grade', field=models.CharField(blank=True, max_length=50, default='')),
        migrations.AddField(model_name='employee', name='region', field=models.CharField(blank=True, max_length=100, default='')),
        migrations.AddField(model_name='employee', name='user_type', field=models.CharField(blank=True, max_length=50, default='', help_text='e.g. User, Backup, TBA, Stock')),
    ]
