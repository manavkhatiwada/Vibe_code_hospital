from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q

from hospitals.models import Hospital
from patients.models import Patient
from .models import Appointment
from .serializers import AppointmentSerializer
from doctors.models import Doctor


class AppointmentViewSet(ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        # Patient: list only their appointments.
        if role == "PATIENT":
            patient_profile, _ = Patient.objects.get_or_create(user=user)
            return (
                Appointment.objects.select_related("doctor", "hospital", "patient", "patient__user")
                .filter(patient=patient_profile)
                .order_by("-appointment_datetime")
            )

        # Doctor: list only appointments where Appointment.doctor matches their Doctor profile.
        if role == "DOCTOR" and hasattr(user, "doctor"):
            return (
                Appointment.objects.select_related("doctor", "hospital", "patient", "patient__user")
                .filter(doctor=user.doctor)
                .order_by("-appointment_datetime")
            )

        # Admin: list appointments for doctors in their hospital.
        if role == "ADMIN" and hasattr(user, "hospital_admin"):
            hospitals = Hospital.objects.filter(admin=user)
            return (
                Appointment.objects.select_related("doctor", "hospital", "patient", "patient__user")
                .filter(
                    Q(hospital__in=hospitals)
                    | Q(doctor__hospital_memberships__hospital__in=hospitals, doctor__hospital_memberships__is_active=True)
                )
                .distinct()
                .order_by("-appointment_datetime")
            )

        return Appointment.objects.none()

    def perform_create(self, serializer):
        if getattr(self.request.user, "role", None) != "PATIENT":
            raise PermissionDenied("Only patients can book appointments.")
        patient_profile, _ = Patient.objects.get_or_create(user=self.request.user)
        serializer.save(patient=patient_profile, status="PENDING")

    def update(self, request, *args, **kwargs):
        raise PermissionDenied("Direct appointment updates are not allowed. Use cancel endpoint.")

    def partial_update(self, request, *args, **kwargs):
        raise PermissionDenied("Direct appointment updates are not allowed. Use cancel endpoint.")

    @action(detail=True, methods=["put"], url_path="cancel")
    def cancel(self, request, pk=None):
        """
        Cancel an appointment.
        - Patients can cancel their own appointments
        - Doctors can cancel their own appointments
        - Hospital-admins can cancel appointments in their hospital
        - Status must not already be CANCELLED or COMPLETED
        """
        appointment = self.get_object()
        user = request.user
        role = getattr(user, "role", None)

        # Check permission based on role
        if role == "PATIENT":
            patient_profile, _ = Patient.objects.get_or_create(user=user)
            if appointment.patient != patient_profile:
                raise PermissionDenied("Patients can only cancel their own appointments.")
        elif role == "DOCTOR":
            if not (hasattr(user, "doctor") and appointment.doctor == user.doctor):
                raise PermissionDenied("Doctors can only cancel their own appointments.")
        elif role == "ADMIN":
            hospitals = Hospital.objects.filter(admin=user)
            if not hospitals.filter(id=appointment.hospital_id).exists():
                raise PermissionDenied("Hospital admins can only cancel appointments in their hospital.")
        else:
            raise PermissionDenied("Only patients, doctors, and hospital admins can cancel appointments.")

        if appointment.status in ["CANCELLED", "COMPLETED"]:
            return Response(
                {"detail": f"Cannot cancel a {appointment.status.lower()} appointment."},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = "CANCELLED"
        appointment.save(update_fields=["status"])
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_200_OK)

        if appointment.status in ["CANCELLED", "COMPLETED"]:
            return Response(
                {"detail": f"Cannot cancel a {appointment.status.lower()} appointment."},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = "CANCELLED"
        appointment.save(update_fields=["status"])
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_path="confirm")
    def confirm(self, request, pk=None):
        """
        Confirm an appointment.
        - Doctors can confirm their own appointments
        - Hospital-admins can confirm appointments in their hospital
        - Appointment must be PENDING to confirm
        """
        appointment = self.get_object()
        user = request.user
        role = getattr(user, "role", None)

        # Check permission based on role
        if role == "DOCTOR":
            if not (hasattr(user, "doctor") and appointment.doctor == user.doctor):
                raise PermissionDenied("Doctors can only confirm their own appointments.")
        elif role == "ADMIN":
            hospitals = Hospital.objects.filter(admin=user)
            if not hospitals.filter(id=appointment.hospital_id).exists():
                raise PermissionDenied("Hospital admins can only confirm appointments in their hospital.")
        else:
            raise PermissionDenied("Only doctors and hospital admins can confirm appointments.")

        if appointment.status != "PENDING":
            return Response(
                {"detail": f"Can only confirm PENDING appointments. Current status: {appointment.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = "CONFIRMED"
        appointment.save(update_fields=["status"])
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_path="reschedule")
    def reschedule(self, request, pk=None):
        """
        Reschedule an appointment to a different date/time.
        - Doctors can reschedule their own appointments
        - Hospital-admins can reschedule appointments in their hospital
        - Request must include new `date` and `time` or `appointment_datetime`
        - Appointment must not be CANCELLED or COMPLETED
        """
        appointment = self.get_object()
        user = request.user
        role = getattr(user, "role", None)

        # Check permission based on role
        if role == "DOCTOR":
            if not (hasattr(user, "doctor") and appointment.doctor == user.doctor):
                raise PermissionDenied("Doctors can only reschedule their own appointments.")
        elif role == "ADMIN":
            hospitals = Hospital.objects.filter(admin=user)
            if not hospitals.filter(id=appointment.hospital_id).exists():
                raise PermissionDenied("Hospital admins can only reschedule appointments in their hospital.")
        else:
            raise PermissionDenied("Only doctors and hospital admins can reschedule appointments.")

        if appointment.status in ["CANCELLED", "COMPLETED"]:
            return Response(
                {"detail": f"Cannot reschedule a {appointment.status.lower()} appointment."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate and extract new appointment datetime from request data
        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_dt = serializer.validated_data.get("appointment_datetime")
        if not validated_dt:
            return Response(
                {"appointment_datetime": "Provide new `appointment_datetime` or `date` + `time` for rescheduling."},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.appointment_datetime = validated_dt
        appointment.save(update_fields=["appointment_datetime"])
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_200_OK)
