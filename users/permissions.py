from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allow only ADMIN role users (or Django superusers/staff)."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(getattr(user, "role", None) == "ADMIN" or user.is_staff or user.is_superuser)
