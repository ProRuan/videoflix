# Third-party suppliers
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Only allow the object's owner."""

    def has_object_permission(self, request, view, obj) -> bool:
        return getattr(obj, "user_id", None) == request.user.id
