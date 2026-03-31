from django.db import migrations


def backfill_patient_profiles(apps, schema_editor):
    User = apps.get_model("users", "User")
    Patient = apps.get_model("patients", "Patient")

    patient_users = User.objects.filter(role="PATIENT")
    for user in patient_users:
        Patient.objects.get_or_create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_role_admin"),
        ("patients", "0003_rename_blood_group"),
    ]

    operations = [
        migrations.RunPython(backfill_patient_profiles, migrations.RunPython.noop),
    ]
