# api/views.py
# Third-party suppliers
from itertools import groupby
from operator import attrgetter
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response

# Local imports
from .permissions import IsAuthenticatedReadOnly
from .serializers import VideoSerializer, VideoDetailSerializer
from video_app.models import Video


class VideoListView(generics.ListAPIView):
    """
    GET /api/videos/
    Returns an array of genre objects, with the special "New on Videoflix"
    genre always first (when there are new videos).
    Each genre object is: { "genre": "<name>", "videos": [ ... ] }.

    Ordering:
      - Top-level genres: alphabetical (except "New on Videoflix" inserted first)
      - Inside each videos array: created_at (newest first), then title (asc)
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticatedReadOnly]

    def list(self, request, *args, **kwargs):
        # configured "new" window (days); default 14
        new_days = getattr(settings, 'VIDEO_NEW_DAYS', 14)
        today = timezone.localdate()
        cutoff = today - timedelta(days=int(new_days))

        # Base queryset ordered for grouping (genre) and then by video ordering
        qs = self.get_queryset().order_by('genre', '-created_at', 'title')

        # Build grouped list by genre
        grouped = []
        for genre, items in groupby(qs, key=attrgetter('genre')):
            vids = list(items)
            serialized = VideoSerializer(
                vids, many=True, context=self.get_serializer_context()
            ).data
            grouped.append({'genre': genre, 'videos': serialized})

        # Build "New on Videoflix" group (new videos across all genres)
        recent_qs = (
            Video.objects.filter(created_at__gte=cutoff)
            .order_by('-created_at', 'title')
        )
        recent_videos = list(recent_qs)
        if recent_videos:
            recent_serialized = VideoSerializer(
                recent_videos, many=True, context=self.get_serializer_context()
            ).data
            # insert as first element
            grouped.insert(0, {'genre': 'New on Videoflix',
                           'videos': recent_serialized})

        return Response(grouped)


class VideoDetailView(generics.RetrieveAPIView):
    """
    GET /api/videos/{pk}/ - retrieve a single video with full fields.
    """
    queryset = Video.objects.all()
    serializer_class = VideoDetailSerializer
    permission_classes = [IsAuthenticatedReadOnly]
