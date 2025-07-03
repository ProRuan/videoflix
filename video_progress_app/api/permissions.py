from video_app.models import Video
from video_progress_app.models import VideoProgress
from rest_framework import serializers
from rest_framework import permissions


class IsOwnerOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
