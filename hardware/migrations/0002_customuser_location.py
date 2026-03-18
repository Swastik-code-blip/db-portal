from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('hardware', '0001_initial'),
    ]
    operations = [
        migrations.AddField(
            model_name='customuser',
            name='location',
            field=models.CharField(blank=True, max_length=100, default='',
                help_text='Leave blank to see ALL locations. Set to restrict to one location.'),
        ),
    ]
