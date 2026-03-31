from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("appointments", "0005_backfill_patient_profile_fk"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="appointment",
            name="patient",
        ),
        migrations.RenameField(
            model_name="appointment",
            old_name="patient_profile",
            new_name="patient",
        ),
        migrations.AlterField(
            model_name="appointment",
            name="patient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="patients.patient",
            ),
        ),
    ]
