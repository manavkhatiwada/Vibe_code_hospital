from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appointments.models import Appointment
from medical_records.models import MedicalRecord
from .models import Patient
from .serializers import PatientBriefSerializer, PatientProfileSerializer


class PatientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_patient(self, request):
        if getattr(request.user, "role", None) != "PATIENT":
            raise PermissionDenied("Only patient users can access patient profile endpoint.")
        patient, _ = Patient.objects.get_or_create(user=request.user)
        return patient

    def get(self, request):
        patient = self._get_patient(request)
        return Response(PatientProfileSerializer(patient).data)

    def put(self, request):
        patient = self._get_patient(request)
        serializer = PatientProfileSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PatientListView(generics.ListAPIView):
    """
    Returns patients for doctor/hospital flows.
    The frontend expects `GET /api/patients/` to return a plain array.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PatientBriefSerializer

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if role == "DOCTOR" and hasattr(user, "doctor"):
            appointment_patient_ids = Appointment.objects.filter(doctor=user.doctor).values_list("patient_id", flat=True)
            record_patient_ids = MedicalRecord.objects.filter(doctor=user.doctor).values_list("patient_id", flat=True)
            patient_ids = set(appointment_patient_ids) | set(record_patient_ids)
            return Patient.objects.select_related("user").filter(id__in=patient_ids).order_by("user__username")

        if role == "ADMIN":
            hospital_ids = user.hospital_admin.values_list("id", flat=True)
            patient_ids = Appointment.objects.filter(hospital_id__in=hospital_ids).values_list("patient_id", flat=True)
            return Patient.objects.select_related("user").filter(id__in=patient_ids).order_by("user__username")

        if role == "PATIENT":
            return Patient.objects.select_related("user").filter(user=user).order_by("user__username")

        return Patient.objects.none()
