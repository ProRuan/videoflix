# Third-party suppliers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter

# Local imports
from .filters import VideoFilter
from .permissions import IsAuthenticatedReadOnly
from .serializers import VideoDetailSerializer, VideoSerializer
from video_app.models import Video


class VideoListView(generics.ListAPIView):
    """
    Represents a video list view for
        - GET /api/videos/
            - list videos
            - filtered by genre
            - sorted newest first
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticatedReadOnly]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = VideoFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class VideoDetailView(generics.RetrieveAPIView):
    """
    Represents a video detail view.
        - GET /api/videos/{pk}/ - retrieve a single video.
    """
    queryset = Video.objects.all()
    serializer_class = VideoDetailSerializer
    permission_classes = [IsAuthenticatedReadOnly]
