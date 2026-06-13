from django.db import migrations, models

from medical_records.models import medical_report_upload_path


def backfill_notes_and_folder(apps, schema_editor):
    MedicalRecord = apps.get_model("medical_records", "MedicalRecord")

    for record in MedicalRecord.objects.all().iterator():
        updates = []

        if not record.folder_name:
            record.folder_name = "General"
            updates.append("folder_name")

        if not record.notes:
            notes_parts = []
            if getattr(record, "diagnosis", ""):
                notes_parts.append(f"Diagnosis: {record.diagnosis}")
            if getattr(record, "prescription", ""):
                notes_parts.append(f"Prescription: {record.prescription}")
            record.notes = "\n".join(notes_parts)
            updates.append("notes")

        if updates:
            record.save(update_fields=updates)


class Migration(migrations.Migration):

    dependencies = [
        ("medical_records", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicalrecord",
            name="notes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="medicalrecord",
            name="folder_name",
            field=models.CharField(default="General", max_length=120),
        ),
        migrations.AlterField(
            model_name="medicalrecord",
            name="diagnosis",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="medicalrecord",
            name="prescription",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="medicalrecord",
            name="report_file",
            field=models.FileField(blank=True, null=True, upload_to=medical_report_upload_path),
        ),
        migrations.RunPython(backfill_notes_and_folder, migrations.RunPython.noop),
    ]