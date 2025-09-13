# Standard libraries
from collections import defaultdict
from datetime import timedelta

# Third-party suppliers
from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Local imports
from ..models import Video
from .serializers import VideoDetailSerializer, VideoListItemSerializer


class VideoListView(APIView):
    """
    GET /api/videos/ -> [{genre, videos}]
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        videos = Video.objects.all().order_by("-created_at", "title")
        new_days = getattr(settings, "VIDEO_NEW_DAYS", 90)
        cutoff = timezone.now() - timedelta(days=new_days)
        new_items = [v for v in videos if v.created_at >= cutoff]
        grouped = defaultdict(list)
        for v in videos:
            grouped[v.genre].append(v)
        payload = []
        if new_items:
            ser = VideoListItemSerializer(new_items, many=True,
                                          context={"request": request})
            payload.append({"genre": "New on Videoflix", "videos": ser.data})
        for genre in sorted(grouped.keys()):
            ser = VideoListItemSerializer(grouped[genre], many=True,
                                          context={"request": request})
            payload.append({"genre": genre, "videos": ser.data})
        return Response(payload)


class VideoDetailView(APIView):
    """
    GET /api/videos/{id}/ -> {video}
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        try:
            video = Video.objects.get(pk=pk)
        except Video.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        data = VideoDetailSerializer(video, context={"request": request}).data
        return Response({"video": data})
