from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Admins can do everything, others can only read.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == "admin":
            return True
        return request.method in SAFE_METHODS


class IsHostOrAdmin(BasePermission):
    """
    Only hosts or admins can create or modify properties.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ["host", "admin"]

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True
        return obj.host == request.user


class IsGuestOrAdmin(BasePermission):
    """
    Only guests or admins can create bookings.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ["guest", "admin"]


class IsOwnerOrAdmin(BasePermission):
    """
    A user can only view or edit their own messages/bookings unless admin.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True
        return getattr(obj, "user", getattr(obj, "sender", None)) == request.user
