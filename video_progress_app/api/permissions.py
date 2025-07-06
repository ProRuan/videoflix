# Third-party suppliers
from rest_framework import permissions


class IsOwnerOnly(permissions.BasePermission):
    """
    Allows only owner of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check user for object permission.
        """
        return obj.user == request.user
