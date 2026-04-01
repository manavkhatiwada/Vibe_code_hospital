from rest_framework import serializers

from users.models import User
from .models import Hospital


class HospitalSerializer(serializers.ModelSerializer):
    admin = serializers.PrimaryKeyRelatedField(read_only=True)
    admin_id = serializers.PrimaryKeyRelatedField(
        source="admin",
        queryset=User.objects.filter(role="ADMIN"),
        write_only=True,
        required=False,
    )

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
            "admin_id",
        ]

    def validate_admin(self, value):
        if value.role != "ADMIN":
            raise serializers.ValidationError("Assigned hospital admin must have ADMIN role.")
        if value.is_staff or value.is_superuser:
            raise serializers.ValidationError("Assigned hospital admin must be a hospital admin account, not super admin.")
        return value
