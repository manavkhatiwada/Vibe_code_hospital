from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "head", "options"]

    def get_queryset(self):
        return (
            Appointment.objects.select_related("doctor", "hospital")
            .filter(patient=self.request.user)
            .order_by("-appintment_datetime")
        )

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user, status="PENDING")

    @action(detail=True, methods=["put"], url_path="cancel")
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status == "CANCELLED":
            return Response(AppointmentSerializer(appointment).data)

        appointment.status = "CANCELLED"
        appointment.save(update_fields=["status"])
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_200_OK)
