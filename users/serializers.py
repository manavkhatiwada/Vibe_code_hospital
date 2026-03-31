from rest_framework import serializers

from doctors.models import Doctor
from hospitals.models import Hospital
from patients.models import Patient

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

    def validate_role(self, value):
        # Public registration is patient-only.
        if value != "PATIENT":
            raise serializers.ValidationError("Public registration is allowed for patients only.")
        return value

    def create(self, validated_data):
        validated_data["role"] = "PATIENT"
        user = User.objects.create_user(
            validated_data["username"],
            validated_data["email"],
            validated_data["password"],
            role=validated_data["role"],
        )

        Patient.objects.get_or_create(user=user)

        return user


class AdminUserCreateSerializer(serializers.ModelSerializer):
    # Required only when creating a doctor account.
    hospital_id = serializers.UUIDField(required=False, write_only=True)
    licence_number = serializers.CharField(required=False, allow_blank=False)
    qualifications = serializers.CharField(required=False, allow_blank=False)
    experience_years = serializers.IntegerField(required=False)
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    specialization = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "role",
            "phone_number",
            "hospital_id",
            "licence_number",
            "qualifications",
            "experience_years",
            "consultation_fee",
            "specialization",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_role(self, value):
        if value not in ["DOCTOR", "ADMIN"]:
            raise serializers.ValidationError("Admin can only create DOCTOR or ADMIN accounts.")
        return value

    def validate(self, attrs):
        role = attrs.get("role")
        if role == "DOCTOR":
            required = [
                "hospital_id",
                "licence_number",
                "qualifications",
                "experience_years",
                "consultation_fee",
            ]
            missing = [field for field in required if attrs.get(field) in [None, ""]]
            if missing:
                raise serializers.ValidationError(
                    {"detail": f"Missing doctor fields: {', '.join(missing)}"}
                )
        return attrs

    def create(self, validated_data):
        hospital_id = validated_data.pop("hospital_id", None)
        licence_number = validated_data.pop("licence_number", None)
        qualifications = validated_data.pop("qualifications", None)
        experience_years = validated_data.pop("experience_years", None)
        consultation_fee = validated_data.pop("consultation_fee", None)
        specialization = validated_data.pop("specialization", "")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data["role"],
            phone_number=validated_data.get("phone_number", ""),
        )

        if user.role == "DOCTOR":
            try:
                hospital = Hospital.objects.get(id=hospital_id)
            except Hospital.DoesNotExist as exc:
                raise serializers.ValidationError({"hospital_id": "Hospital not found."}) from exc

            Doctor.objects.create(
                user=user,
                hospital=hospital,
                specialization=specialization,
                licence_number=licence_number,
                qualifications=qualifications,
                experience_years=experience_years,
                consultation_fee=consultation_fee,
            )

        return user
