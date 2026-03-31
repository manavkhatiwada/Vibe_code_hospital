from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("patients", "0004_backfill_patient_profiles"),
        ("appointments", "0003_rename_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="appointment",
            name="patient_profile",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="patients.patient",
            ),
        ),
    ]
