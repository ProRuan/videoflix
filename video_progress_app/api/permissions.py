# Third-party suppliers
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Only the object´s owner has the permission to maintain the object.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """Check a user for having object permission."""
        return getattr(obj, "user_id", None) == request.user.id
