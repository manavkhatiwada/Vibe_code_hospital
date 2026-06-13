from rest_framework import serializers

from doctors.models import Doctor
from patients.models import Patient

from .models import MedicalRecord


class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    Payload contract:
    - Patient creates: { doctor, notes, folder_name?, report_file? }
    - Doctor creates:  { patient, notes, folder_name?, report_file? }
    The backend assigns missing `patient`/`doctor` from `request.user`.
    """

    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), required=False, allow_null=True)
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), required=False)
    notes = serializers.CharField()
    folder_name = serializers.CharField(required=False, allow_blank=True, max_length=120)
    is_private = serializers.BooleanField(default=True, required=False)
    shared_with = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    report_file = serializers.FileField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "patient",
            "doctor",
            "appointment",
            "folder_name",
            "notes",
            "is_private",
            "shared_with",
            "report_file",
            "created_at",
        ]
        read_only_fields = ["id", "shared_with", "created_at"]

    def validate_folder_name(self, value):
        folder_name = (value or "").strip()
        return folder_name or "General"
