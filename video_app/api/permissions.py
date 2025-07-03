from rest_framework import permissions


class IsAuthenticatedReadOnly(permissions.BasePermission):
    """
    Allow only authenticated users to perform SAFE_METHODS (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return False
