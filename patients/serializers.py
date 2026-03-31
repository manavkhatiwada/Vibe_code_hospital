import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Patient

User = get_user_model()


class PatientProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    age = serializers.SerializerMethodField(read_only=True)

    def get_age(self, obj):
        if not obj.date_of_birth:
            return None
        today = datetime.date.today()
        return today.year - obj.date_of_birth.year - (
            (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
        )

    class Meta:
        model = Patient
        fields = [
            "id",
            "user",
            "date_of_birth",
            "age",
            "gender",
            "blood_group",
            "emergency_contact_name",
            "insurance_number",
        ]


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class PatientBriefSerializer(serializers.ModelSerializer):
    """
    Minimal patient payload used by the frontend (doctor pages).
    """

    user = UserBriefSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ["id", "user"]
