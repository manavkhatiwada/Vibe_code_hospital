from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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
                .filter(hospital__in=hospitals)
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
        appointment = self.get_object()
        if appointment.status == "CANCELLED":
            return Response(AppointmentSerializer(appointment).data)

        appointment.status = "CANCELLED"
        appointment.save(update_fields=["status"])
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_200_OK)
