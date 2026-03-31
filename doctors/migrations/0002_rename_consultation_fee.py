# Generated migration to rename doctor consultation_fee field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doctor',
            old_name='consulataion_fee',
            new_name='consultation_fee',
        ),
    ]
