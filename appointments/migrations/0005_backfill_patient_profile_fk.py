from django.db import migrations


def backfill_patient_profile_fk(apps, schema_editor):
    Appointment = apps.get_model("appointments", "Appointment")
    Patient = apps.get_model("patients", "Patient")

    for appt in Appointment.objects.all().iterator():
        user_id = getattr(appt, "patient_id", None)
        if not user_id:
            continue
        patient_profile, _ = Patient.objects.get_or_create(user_id=user_id)
        appt.patient_profile_id = patient_profile.id
        appt.save(update_fields=["patient_profile"])


class Migration(migrations.Migration):

    dependencies = [
        ("appointments", "0004_add_patient_profile_fk"),
    ]

    operations = [
        migrations.RunPython(backfill_patient_profile_fk, migrations.RunPython.noop),
    ]
