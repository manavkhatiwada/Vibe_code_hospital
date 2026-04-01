from rest_framework.permissions import BasePermission


def is_super_admin_user(user):
    if not user or not user.is_authenticated:
        return False
    # Platform-level admin is explicitly tied to Django superuser flag.
    return bool(getattr(user, "role", None) == "ADMIN" and user.is_superuser)


class IsAdminRole(BasePermission):
    """Allow only ADMIN role users (or Django superusers/staff)."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(getattr(user, "role", None) == "ADMIN" or user.is_staff or user.is_superuser)


class IsSuperAdmin(BasePermission):
    """Allow only platform-level super admin users."""

    def has_permission(self, request, view):
        return is_super_admin_user(request.user)


class IsHospitalAdmin(BasePermission):
    """Allow only hospital admins (ADMIN role but not platform super admin)."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "role", None) != "ADMIN":
            return False
        return not is_super_admin_user(user)


class IsPatientRole(BasePermission):
    """Allow only authenticated PATIENT role users."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(getattr(user, "role", None) == "PATIENT")
