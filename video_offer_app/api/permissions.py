from rest_framework.permissions import BasePermission, SAFE_METHODS


# do I need bool() here?
# try class below + testing!
class IsAdminOrReadOnly(BasePermission):
    """
    Allow anyone to read, but only staff to create.
    """

    def has_permission(self, request, view):
        # Allow GET/HEAD/OPTIONS for everyone
        if request.method in SAFE_METHODS:
            return True
        # For POST (and other unsafe methods), require authenticated staff
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


# from rest_framework.permissions import BasePermission, SAFE_METHODS


# class IsAdminOrReadOnly(BasePermission):
#     """
#     Allow read-only access to anyone, but write/delete only to staff users.
#     """

#     def has_permission(self, request, view):
#         if request.method in SAFE_METHODS:
#             return True
#         return request.user and request.user.is_authenticated and request.user.is_staff
