# Generated migration to rename patient blood_group field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0002_alter_patient_bloood_group_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patient',
            old_name='bloood_group',
            new_name='blood_group',
        ),
    ]
