# api/views.py
# Third-party suppliers
from itertools import groupby
from operator import attrgetter

from rest_framework import generics
from rest_framework.response import Response

# Local imports
from .permissions import IsAuthenticatedReadOnly
from .serializers import VideoSerializer, VideoDetailSerializer
from video_app.models import Video


class VideoListView(generics.ListAPIView):
    """
    GET /api/videos/
    Returns an array of genres sorted alphabetically. Each genre contains
    a `videos` array sorted by created_at (newest first) then title (ascending).
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticatedReadOnly]

    def list(self, request, *args, **kwargs):
        # order by genre (for grouping), then created_at desc, then title asc
        qs = self.get_queryset().order_by('genre', '-created_at', 'title')
        grouped = []
        for genre, items in groupby(qs, key=attrgetter('genre')):
            vids = list(items)
            serialized = VideoSerializer(
                vids, many=True, context=self.get_serializer_context()
            ).data
            grouped.append({'genre': genre, 'videos': serialized})
        return Response(grouped)


class VideoDetailView(generics.RetrieveAPIView):
    """
    GET /api/videos/{pk}/ - retrieve a single video with full fields.
    """
    queryset = Video.objects.all()
    serializer_class = VideoDetailSerializer
    permission_classes = [IsAuthenticatedReadOnly]
