from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from doctors.models import Doctor, DoctorHospitalMembership
from hospitals.models import Hospital
from users.models import User


class Command(BaseCommand):
    help = "Attach a real Doctor profile to an existing DOCTOR user without dummy values."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Doctor user's email")
        parser.add_argument("--hospital-id", required=True, help="Hospital UUID")
        parser.add_argument("--licence-number", required=True)
        parser.add_argument("--qualifications", required=True)
        parser.add_argument("--experience-years", type=int, required=True)
        parser.add_argument("--consultation-fee", required=True)
        parser.add_argument("--specialization", default="", required=False)

    def handle(self, *args, **options):
        email = options["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as exc:
            raise CommandError(f"User not found: {email}") from exc

        if user.role != "DOCTOR":
            raise CommandError(f"User {email} is role={user.role}, expected DOCTOR")

        if Doctor.objects.filter(user=user).exists():
            raise CommandError(f"User {email} already has a Doctor profile")

        try:
            hospital = Hospital.objects.get(id=options["hospital_id"])
        except Hospital.DoesNotExist as exc:
            raise CommandError("Hospital not found") from exc

        doctor = Doctor.objects.create(
            user=user,
            hospital=hospital,
            specialization=options["specialization"],
            licence_number=options["licence_number"],
            qualifications=options["qualifications"],
            experience_years=options["experience_years"],
            consultation_fee=Decimal(str(options["consultation_fee"])),
        )
        DoctorHospitalMembership.objects.get_or_create(
            doctor=doctor,
            hospital=hospital,
            defaults={"is_active": True},
        )

        self.stdout.write(self.style.SUCCESS(f"Doctor profile attached for {email}"))
