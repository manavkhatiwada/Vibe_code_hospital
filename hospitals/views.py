from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Hospital
from .serializers import HospitalSerializer


class HospitalViewSet(ModelViewSet):
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Hospital.objects.all().order_by("name")

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)
