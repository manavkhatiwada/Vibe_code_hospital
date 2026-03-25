from rest_framework import serializers

from .models import Hospital


class HospitalSerializer(serializers.ModelSerializer):
    admin = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Hospital
        fields = [
            "id",
            "name",
            "registration_number",
            "address",
            "city",
            "state",
            "country",
            "contact_email",
            "contact_phone",
            "admin",
        ]
