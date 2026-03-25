from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    # Normalize awkward model field names to a clean API.
    id = serializers.UUIDField(source="ID", read_only=True)
    appointment_datetime = serializers.DateTimeField(source="appintment_datetime")
    patient = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.ChoiceField(choices=Appointment.STATUS_CHOICES, read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "doctor",
            "hospital",
            "appointment_datetime",
            "status",
            "reason",
        ]

    def validate(self, attrs):
        doctor = attrs.get("doctor")
        hospital = attrs.get("hospital")
        if doctor and hospital and doctor.hospital_id != hospital.id:
            raise serializers.ValidationError(
                {"hospital": "Hospital must match the doctor's hospital."}
            )
        return attrs

