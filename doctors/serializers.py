from rest_framework import serializers

from hospitals.models import Hospital

from .models import Doctor


class HospitalBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ["id", "name", "city", "state", "country"]


class DoctorSerializer(serializers.ModelSerializer):
    hospital = HospitalBriefSerializer(read_only=True)
    hospitals = serializers.SerializerMethodField(read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Doctor
        fields = [
            "id",
            "user_email",
            "user_username",
            "hospital",
            "hospitals",
            "specialization",
            "licence_number",
            "qualifications",
            "experience_years",
            "consultation_fee",
        ]

    def get_hospitals(self, obj):
        memberships = obj.hospital_memberships.select_related("hospital").filter(is_active=True)
        if memberships.exists():
            return HospitalBriefSerializer([m.hospital for m in memberships], many=True).data

        # Backward compatibility for rows not migrated yet.
        if obj.hospital_id:
            return HospitalBriefSerializer([obj.hospital], many=True).data
        return []

