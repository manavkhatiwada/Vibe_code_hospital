from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db.models import Q

from appointments.models import Appointment
from doctors.models import Doctor
from hospitals.models import Hospital
from patients.models import Patient

from .models import MedicalRecord
from .serializers import MedicalRecordSerializer

class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def _get_patient_profile(self, user):
        """
        Ensure the Patient profile exists for `role=PATIENT`.
        This keeps `/api/records/` functional right after login.
        """

        patient, _ = Patient.objects.get_or_create(user=user)
        return patient

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_superuser', False):
            return MedicalRecord.objects.all()

        role = getattr(user, "role", None)

        # Doctor users: list by their Doctor profile.
        try:
            if role == "DOCTOR" and hasattr(user, "doctor"):
                return MedicalRecord.objects.select_related(
                    "patient", "patient__user", "doctor", "doctor__user", "appointment"
                ).filter(doctor=user.doctor)
        except Exception:
            pass

        # Patient users: ensure Patient profile exists and list by it.
        try:
            if role == "PATIENT":
                patient_profile = self._get_patient_profile(user)
                return MedicalRecord.objects.select_related(
                    "patient", "patient__user", "doctor", "doctor__user", "appointment"
                ).filter(patient=patient_profile)
        except Exception:
            pass

        # Admin users: list records for doctors that belong to their hospital.
        try:
            if role == "ADMIN":
                hospitals = Hospital.objects.filter(admin=user)
                return MedicalRecord.objects.select_related(
                    "patient", "patient__user", "doctor", "doctor__user", "appointment"
                ).filter(
                    Q(doctor__hospital__in=hospitals)
                    | Q(doctor__hospital_memberships__hospital__in=hospitals, doctor__hospital_memberships__is_active=True)
                ).distinct()
        except Exception:
            pass

        return MedicalRecord.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        role = getattr(user, "role", None)
        appointment_id = self.request.data.get("appointment")

        def _get_appointment_or_none():
            if not appointment_id:
                return None
            try:
                return Appointment.objects.select_related("patient", "doctor").get(pk=appointment_id)
            except Appointment.DoesNotExist as exc:
                raise ValidationError({"appointment": "Appointment not found."}) from exc

        # Patient creates a record: backend assigns `patient` from request.user
        # and requires `doctor` from the payload.
        if role == "PATIENT":
            patient_profile = self._get_patient_profile(user)
            doctor_id = self.request.data.get("doctor")
            if not doctor_id:
                raise ValidationError({"doctor": "Doctor is required to upload a medical record."})

            try:
                doctor = Doctor.objects.get(pk=doctor_id)
            except Doctor.DoesNotExist as exc:
                raise ValidationError({"doctor": "Doctor not found."}) from exc

            appointment = _get_appointment_or_none()
            if appointment:
                if appointment.patient_id != patient_profile.id:
                    raise PermissionDenied("You can only link your own appointments.")
                if appointment.doctor_id != doctor.id:
                    raise ValidationError({"appointment": "Appointment doctor does not match selected doctor."})

            serializer.save(patient=patient_profile, doctor=doctor, appointment=appointment)
            return

        # Doctor creates a record: backend assigns `doctor` from request.user
        # and requires `patient` from the payload.
        if role == "DOCTOR":
            if not hasattr(user, "doctor"):
                raise PermissionDenied("Doctor profile missing.")

            patient_id = self.request.data.get("patient")
            if not patient_id:
                raise ValidationError({"patient": "Patient is required to create a medical record."})

            try:
                patient_profile = Patient.objects.get(pk=patient_id)
            except Patient.DoesNotExist as exc:
                raise ValidationError({"patient": "Patient not found."}) from exc

            appointment = _get_appointment_or_none()
            if appointment:
                if appointment.patient_id != patient_profile.id or appointment.doctor_id != user.doctor.id:
                    raise ValidationError(
                        {"appointment": "Appointment must belong to the selected patient and logged-in doctor."}
                    )
            else:
                has_relationship = Appointment.objects.filter(
                    patient=patient_profile,
                    doctor=user.doctor,
                ).exists() or MedicalRecord.objects.filter(
                    patient=patient_profile,
                    doctor=user.doctor,
                ).exists()
                if not has_relationship:
                    raise PermissionDenied(
                        "You can only create records for patients assigned to you via appointment or existing record."
                    )

            serializer.save(patient=patient_profile, doctor=user.doctor, appointment=appointment)
            return

        raise PermissionDenied("Only patients and doctors can create medical records.")
