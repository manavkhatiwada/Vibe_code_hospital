from django.core.management.base import BaseCommand, CommandError

from doctors.models import Doctor
from patients.models import Patient
from users.models import User


class Command(BaseCommand):
    help = "Ensure PATIENT users have Patient profiles and report missing Doctor profiles."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fail-on-missing-doctor",
            action="store_true",
            help="Exit with error if any DOCTOR user is missing Doctor profile.",
        )

    def handle(self, *args, **options):
        created_patients = 0

        patient_users = User.objects.filter(role="PATIENT")
        for user in patient_users:
            _, created = Patient.objects.get_or_create(user=user)
            if created:
                created_patients += 1

        doctor_users = User.objects.filter(role="DOCTOR")
        missing_doctor_profiles = doctor_users.exclude(id__in=Doctor.objects.values_list("user_id", flat=True))

        self.stdout.write(
            self.style.SUCCESS(
                f"Patient profiles ensured. Created missing profiles: {created_patients}"
            )
        )

        if missing_doctor_profiles.exists():
            missing_emails = ", ".join(missing_doctor_profiles.values_list("email", flat=True))
            msg = f"Doctor users missing Doctor profile: {missing_emails}"
            if options["fail_on_missing_doctor"]:
                raise CommandError(msg)
            self.stdout.write(self.style.WARNING(msg))
        else:
            self.stdout.write(self.style.SUCCESS("All DOCTOR users have Doctor profiles."))
