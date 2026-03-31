from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from .models import Doctor
from .serializers import DoctorSerializer
from hospitals.models import Hospital


class DoctorViewSet(ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "delete", "head", "options"]

    def get_queryset(self):
        qs = Doctor.objects.select_related("user", "hospital").all()
        user = getattr(self.request, "user", None)
        role = getattr(user, "role", None)

        # Admin users can only manage doctors in their own hospital.
        if role == "ADMIN":
            hospitals = Hospital.objects.filter(admin=user)
            return qs.filter(hospital__in=hospitals)

        # Doctors can view only themselves.
        if role == "DOCTOR" and hasattr(user, "doctor"):
            return qs.filter(id=user.doctor.id)

        # Patients can browse doctors for booking.
        if role == "PATIENT":
            return qs

        return qs.none()

    def create(self, request, *args, **kwargs):
        raise PermissionDenied("Use /api/admin/users/ to create doctor accounts.")

    def update(self, request, *args, **kwargs):
        raise PermissionDenied("Doctor profile updates are not allowed via this endpoint.")

    def partial_update(self, request, *args, **kwargs):
        raise PermissionDenied("Doctor profile updates are not allowed via this endpoint.")

    def destroy(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != "ADMIN":
            raise PermissionDenied("Only admins can remove doctors.")
        return super().destroy(request, *args, **kwargs)
