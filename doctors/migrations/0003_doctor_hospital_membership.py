from django.conf import settings
from django.db import migrations, models


def backfill_doctor_hospital_memberships(apps, schema_editor):
    Doctor = apps.get_model("doctors", "Doctor")
    DoctorHospitalMembership = apps.get_model("doctors", "DoctorHospitalMembership")

    for doctor in Doctor.objects.exclude(hospital_id__isnull=True).iterator():
        DoctorHospitalMembership.objects.get_or_create(
            doctor_id=doctor.id,
            hospital_id=doctor.hospital_id,
            defaults={"is_active": True},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("hospitals", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("doctors", "0002_rename_consultation_fee"),
    ]

    operations = [
        migrations.CreateModel(
            name="DoctorHospitalMembership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("linked_at", models.DateTimeField(auto_now_add=True)),
                (
                    "doctor",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="hospital_memberships",
                        to="doctors.doctor",
                    ),
                ),
                (
                    "hospital",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="doctor_memberships",
                        to="hospitals.hospital",
                    ),
                ),
                (
                    "linked_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="created_doctor_hospital_links",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"unique_together": {("doctor", "hospital")}},
        ),
        migrations.AddField(
            model_name="doctor",
            name="hospitals",
            field=models.ManyToManyField(
                blank=True,
                related_name="linked_doctors",
                through="doctors.DoctorHospitalMembership",
                to="hospitals.hospital",
            ),
        ),
        migrations.RunPython(
            backfill_doctor_hospital_memberships,
            migrations.RunPython.noop,
        ),
    ]
