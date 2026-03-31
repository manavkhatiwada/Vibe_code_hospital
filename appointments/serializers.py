import datetime

from django.utils import timezone
from rest_framework import serializers

from doctors.models import Doctor
from hospitals.models import Hospital
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    # Normalize awkward model field names to a clean API.
    appointment_datetime = serializers.DateTimeField(required=False)
    date = serializers.DateField(write_only=True, required=False)
    time = serializers.TimeField(write_only=True, required=False)
    doctor_name = serializers.SerializerMethodField(read_only=True)
    patient_name = serializers.SerializerMethodField(read_only=True)

    patient = serializers.PrimaryKeyRelatedField(read_only=True)
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), required=True)
    hospital = serializers.PrimaryKeyRelatedField(
        queryset=Hospital.objects.all(), required=False, allow_null=True
    )

    status = serializers.ChoiceField(choices=Appointment.STATUS_CHOICES, read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "hospital",
            "appointment_datetime",
            "date",
            "time",
            "status",
            "reason",
        ]

    def get_doctor_name(self, obj):
        return getattr(getattr(obj.doctor, "user", None), "username", None)

    def get_patient_name(self, obj):
        return getattr(getattr(obj.patient, "user", None), "username", None)

    def validate(self, attrs):
        doctor = attrs.get("doctor")
        hospital = attrs.get("hospital")

        # Accept frontend payload (`date` + `time`) and convert to
        # `appointment_datetime`.
        input_date = attrs.pop("date", None)
        input_time = attrs.pop("time", None)

        if doctor and not hospital:
            attrs["hospital"] = doctor.hospital
        if doctor and hospital and doctor.hospital_id != hospital.id:
            raise serializers.ValidationError(
                {"hospital": "Hospital must match the doctor's hospital."}
            )

        # If `appointment_datetime` wasn't provided, build it from `date` + `time`.
        appointment_dt = attrs.get("appointment_datetime")
        if not appointment_dt and input_date and input_time:
            combined = datetime.datetime.combine(input_date, input_time)
            attrs["appointment_datetime"] = timezone.make_aware(
                combined, timezone.get_current_timezone()
            )
        elif not appointment_dt:
            raise serializers.ValidationError(
                {"appointment_datetime": "Provide either `appointment_datetime` or `date` + `time`."}
            )
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        dt = getattr(instance, "appointment_datetime", None)
        if dt:
            rep["date"] = dt.date().isoformat()
            rep["time"] = dt.time().isoformat(timespec="seconds")
        return rep

