from rest_framework import generics, permissions
from video_progress_app.models import VideoProgress
from .serializers import VideoProgressSerializer
from .permissions import IsOwnerOnly


class VideoProgressListCreateView(generics.ListCreateAPIView):
    """
    GET /api/video-progress/  List authenticated user's video progress (newest first)
    POST /api/video-progress/ Create a new video progress entry
    """
    serializer_class = VideoProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VideoProgress.objects.filter(user=self.request.user).order_by('-updated_at')


class VideoProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/video-progress/{id}/
    """
    serializer_class = VideoProgressSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOnly]

    def get_queryset(self):
        return VideoProgress.objects.filter(user=self.request.user)
