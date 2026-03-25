from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Doctor
from .serializers import DoctorSerializer


class DoctorViewSet(ReadOnlyModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Doctor.objects.select_related("user", "hospital").all()
