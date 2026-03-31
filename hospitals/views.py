from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from .models import Hospital
from .serializers import HospitalSerializer


class HospitalViewSet(ModelViewSet):
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if role == "ADMIN":
            return Hospital.objects.filter(admin=user).order_by("name")

        if role == "DOCTOR" and hasattr(user, "doctor"):
            return Hospital.objects.filter(id=user.doctor.hospital_id).order_by("name")

        return Hospital.objects.none()

    def perform_create(self, serializer):
        if getattr(self.request.user, "role", None) != "ADMIN":
            raise PermissionDenied("Only admins can create hospitals.")
        serializer.save(admin=self.request.user)
