from rest_framework import serializers

from .models import Patient


class PatientProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "user",
            "date_of_birth",
            "gender",
            "bloood_group",
            "emergency_contact_name",
            "insurance_number",
        ]
