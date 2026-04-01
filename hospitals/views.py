from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Hospital
from .serializers import HospitalSerializer
from users.permissions import is_super_admin_user
from doctors.models import Doctor, DoctorHospitalMembership
from doctors.serializers import DoctorSerializer


class HospitalViewSet(ModelViewSet):
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if is_super_admin_user(user):
            return Hospital.objects.all().order_by("name")

        if role == "ADMIN":
            return Hospital.objects.filter(admin=user).order_by("name")

        if role == "DOCTOR" and hasattr(user, "doctor"):
            return Hospital.objects.filter(id=user.doctor.hospital_id).order_by("name")

        return Hospital.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not is_super_admin_user(user):
            raise PermissionDenied("Only super admins can create hospitals.")

        if "admin" not in serializer.validated_data:
            raise PermissionDenied("Hospital creation requires assigning a hospital admin account.")

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        if not is_super_admin_user(request.user):
            raise PermissionDenied("Only super admins can delete hospitals.")
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="link-doctor")
    def link_doctor(self, request, pk=None):
        """
        Link a doctor to this hospital.
        - Hospital-admin can link doctors to their hospital
        - Super-admin can link to any hospital
        - Creates DoctorHospitalMembership entry
        - Request body: {"doctor_id": "uuid"}
        """
        hospital = self.get_object()
        user = request.user
        role = getattr(user, "role", None)

        # Check permission: only super-admin or this hospital's admin
        if not (is_super_admin_user(user) or hospital.admin == user):
            raise PermissionDenied("Only super-admins or this hospital's admin can link doctors.")

        doctor_id = request.data.get("doctor_id")
        if not doctor_id:
            return Response(
                {"detail": "Request body must include 'doctor_id'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response(
                {"detail": f"Doctor {doctor_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create or update membership
        membership, created = DoctorHospitalMembership.objects.get_or_create(
            doctor=doctor,
            hospital=hospital,
            defaults={"is_active": True, "linked_by": user}
        )

        if not created:
            # If it already exists, ensure it's active
            if not membership.is_active:
                membership.is_active = True
                membership.save(update_fields=["is_active"])
            return Response(
                {"detail": f"Doctor {doctor.user.username} is already linked to {hospital.name}."},
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "detail": f"Doctor {doctor.user.username} successfully linked to {hospital.name}.",
                "membership_id": membership.id,
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["delete"], url_path="unlink-doctor")
    def unlink_doctor(self, request, pk=None):
        """
        Unlink a doctor from this hospital (soft-delete via is_active=False).
        - Hospital-admin can unlink doctors from their hospital
        - Super-admin can unlink from any hospital
        - Request body: {"doctor_id": "uuid"} or query param: ?doctor_id=uuid
        """
        hospital = self.get_object()
        user = request.user
        role = getattr(user, "role", None)

        # Check permission: only super-admin or this hospital's admin
        if not (is_super_admin_user(user) or hospital.admin == user):
            raise PermissionDenied("Only super-admins or this hospital's admin can unlink doctors.")

        # Get doctor_id from request body or query params
        doctor_id = request.data.get("doctor_id") or request.query_params.get("doctor_id")
        if not doctor_id:
            return Response(
                {"detail": "Provide 'doctor_id' in request body or as query parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            membership = DoctorHospitalMembership.objects.get(
                doctor_id=doctor_id,
                hospital_id=hospital.id
            )
        except DoctorHospitalMembership.DoesNotExist:
            return Response(
                {"detail": f"Doctor is not linked to {hospital.name}."},
                status=status.HTTP_404_NOT_FOUND
            )

        doctor_name = membership.doctor.user.username
        membership.is_active = False
        membership.save(update_fields=["is_active"])
        
        return Response(
            {"detail": f"Doctor {doctor_name} has been unlinked from {hospital.name}."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"], url_path="linked-doctors")
    def linked_doctors(self, request, pk=None):
        """
        Get all doctors currently linked to this hospital.
        - Hospital-admin can view doctors in their hospital
        - Super-admin can view doctors in any hospital
        - Patients can browse all doctors
        """
        hospital = self.get_object()
        user = request.user
        role = getattr(user, "role", None)

        # Permission check
        if role == "ADMIN" and hospital.admin != user:
            raise PermissionDenied("Hospital admins can only view doctors in their own hospital.")

        # Get active memberships for this hospital
        memberships = DoctorHospitalMembership.objects.filter(
            hospital=hospital,
            is_active=True
        ).select_related("doctor__user")

        doctors = [membership.doctor for membership in memberships]
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="available-doctors")
    def available_doctors(self, request, pk=None):
        """
        Get doctors that can be linked to this hospital.
        - Shows doctors not yet linked to this hospital
        - Hospital-admin can view for their hospital
        - Super-admin can view for any hospital
        """
        hospital = self.get_object()
        user = request.user
        role = getattr(user, "role", None)

        # Permission check
        if role == "ADMIN" and hospital.admin != user:
            raise PermissionDenied("Hospital admins can only view doctors for their own hospital.")

        # Get doctors not yet linked to this hospital (or linked but inactive)
        linked_ids = DoctorHospitalMembership.objects.filter(
            hospital=hospital,
            is_active=True
        ).values_list("doctor_id", flat=True)

        available = Doctor.objects.exclude(id__in=linked_ids).select_related("user")
        serializer = DoctorSerializer(available, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
