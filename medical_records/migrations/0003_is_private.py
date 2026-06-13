from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("medical_records", "0002_notes_folder_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicalrecord",
            name="is_private",
            field=models.BooleanField(default=True, help_text="If True, only patient can see. If False, can be shared with doctors."),
        ),
    ]
