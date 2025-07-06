# Third-party suppliers
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

# Local imports
from .permissions import IsOwnerOnly
from .serializers import VideoProgressSerializer
from video_progress_app.models import VideoProgress


class VideoProgressListCreateView(generics.ListCreateAPIView):
    """
    Represents a video progress list-create view for /api/video-progress/.
        - GET: List authenticated user´s video progress.
        - POST: Create an new video progress entry.
    """
    serializer_class = VideoProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get queryset of authenticated user´s video progress only.
        """
        obj_unsorted = VideoProgress.objects.filter(user=self.request.user)
        return obj_unsorted.order_by('-updated_at')


class VideoProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Represents a video progress detail view for /api/video-progress/{id}/.
        - GET: Returns the video progress of an authenticated user´s video.
        - PATCH: Update the video progress of an authenticated user´s video.
        - DELETE: Deletes the video progress of an authenticated user`s video.
    """
    serializer_class = VideoProgressSerializer
    permission_classes = [IsAuthenticated, IsOwnerOnly]
    queryset = VideoProgress.objects.all()
