from django.core.management.base import BaseCommand, CommandError

from doctors.models import Doctor
from doctors.models import DoctorHospitalMembership
from hospitals.models import Hospital
from patients.models import Patient
from users.models import User


class Command(BaseCommand):
    help = "Ensure profile integrity and validate hospital/doctor access relationships."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fail-on-missing-doctor",
            action="store_true",
            help="Exit with error if any DOCTOR user is missing Doctor profile.",
        )
        parser.add_argument(
            "--fix-missing-memberships",
            action="store_true",
            help="Create active doctor-hospital memberships from legacy Doctor.hospital where missing.",
        )
        parser.add_argument(
            "--fail-on-admin-violations",
            action="store_true",
            help="Exit with error when hospitals have invalid admin assignments.",
        )
        parser.add_argument(
            "--fail-on-missing-membership",
            action="store_true",
            help="Exit with error when any doctor has no active hospital membership.",
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

        hospitals = Hospital.objects.select_related("admin").all()
        invalid_admin_hospitals = []
        for hospital in hospitals:
            admin = hospital.admin
            if admin.role != "ADMIN" or admin.is_superuser:
                invalid_admin_hospitals.append(hospital)

        doctors = Doctor.objects.select_related("hospital", "user")
        missing_membership_doctors = []
        created_memberships = 0
        for doctor in doctors:
            has_active_membership = doctor.hospital_memberships.filter(is_active=True).exists()
            if has_active_membership:
                continue

            missing_membership_doctors.append(doctor)
            if options["fix_missing_memberships"]:
                membership, created = DoctorHospitalMembership.objects.get_or_create(
                    doctor=doctor,
                    hospital=doctor.hospital,
                    defaults={"is_active": True},
                )
                if not membership.is_active:
                    membership.is_active = True
                    membership.save(update_fields=["is_active"])
                    created = True
                if created:
                    created_memberships += 1

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

        if invalid_admin_hospitals:
            names = ", ".join([h.name for h in invalid_admin_hospitals])
            msg = (
                "Hospitals with invalid admin assignment (admin must be role=ADMIN and not superuser): "
                f"{names}"
            )
            if options["fail_on_admin_violations"]:
                raise CommandError(msg)
            self.stdout.write(self.style.WARNING(msg))
        else:
            self.stdout.write(self.style.SUCCESS("All hospitals have valid hospital-admin assignments."))

        if missing_membership_doctors:
            emails = ", ".join([d.user.email for d in missing_membership_doctors])
            msg = f"Doctors missing active hospital membership: {emails}"
            if options["fix_missing_memberships"]:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Backfill executed. Created memberships: {created_memberships}"
                    )
                )
            remaining_missing = Doctor.objects.exclude(
                hospital_memberships__is_active=True
            ).count()
            if options["fail_on_missing_membership"] and remaining_missing > 0:
                raise CommandError(msg)
            if not options["fix_missing_memberships"]:
                self.stdout.write(self.style.WARNING(msg))
        else:
            self.stdout.write(self.style.SUCCESS("All doctors have at least one active hospital membership."))
