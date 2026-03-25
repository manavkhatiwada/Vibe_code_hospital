from rest_framework import serializers
from .models import User

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "role", "phone_number", "is_verified"]


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Django's `UserManager.create_user()` hashes the password (make_password)
        # before saving.
        return User.objects.create_user(
            validated_data["username"],
            validated_data["email"],
            validated_data["password"],
            role=validated_data["role"],
        )