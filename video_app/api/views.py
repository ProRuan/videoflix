from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from video_app.models import Video
from .serializers import VideoSerializer
from .permissions import IsAuthenticatedReadOnly
from .filters import VideoFilter
from .paginations import VideoPagination


class VideoListView(generics.ListAPIView):
    """
    GET /api/videos/ - list videos, paginated, filtered by genre, sorted newest-first.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticatedReadOnly]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = VideoFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    pagination_class = VideoPagination


class VideoDetailView(generics.RetrieveAPIView):
    """
    GET /api/videos/{pk}/ - retrieve a single video.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticatedReadOnly]
