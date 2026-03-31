# Generated migration to rename appointment fields

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_alter_appointment_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='appintment_datetime',
            new_name='appointment_datetime',
        ),
        migrations.RenameField(
            model_name='appointment',
            old_name='ID',
            new_name='id',
        ),
    ]
