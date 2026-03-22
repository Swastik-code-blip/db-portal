from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('hardware', '0008_message_model'),
    ]
    operations = [
        migrations.AddField(
            model_name='hardwaretype',
            name='custom_fields',
            field=models.TextField(blank=True, default='', help_text='JSON list of field names'),
        ),
    ]
