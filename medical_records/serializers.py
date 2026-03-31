from rest_framework import serializers

from doctors.models import Doctor
from patients.models import Patient

from .models import MedicalRecord


class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    Payload contract:
    - Patient creates: { doctor, diagnosis, prescription, report_file? }
    - Doctor creates:  { patient, diagnosis, prescription, report_file? }
    The backend assigns missing `patient`/`doctor` from `request.user`.
    """

    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), required=False)
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), required=False)

    report_file = serializers.FileField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "patient",
            "doctor",
            "appointment",
            "diagnosis",
            "prescription",
            "report_file",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
