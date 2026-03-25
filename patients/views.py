from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Patient
from .serializers import PatientProfileSerializer


class PatientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_patient(self, request):
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
