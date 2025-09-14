# Standard libraries
from collections import defaultdict
from datetime import timedelta

# Third-party suppliers
from django.conf import settings
from django.db.models import OuterRef, Subquery
from django.utils import timezone
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from ..models import Video
from .serializers import VideoDetailSerializer, VideoListItemSerializer
from video_progress_app.models import VideoProgress


class VideoListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vp = VideoProgress.objects.filter(
            user_id=request.user.id, video_id=OuterRef("pk")
        )
        videos = (Video.objects.all().order_by("-created_at", "title")
                  .annotate(progress_id=Subquery(vp.values("id")[:1]),
                            relative_position=Subquery(
                                vp.values("relative_position")[:1])))

        new_days = getattr(settings, "VIDEO_NEW_DAYS", 90)
        cutoff = timezone.now() - timedelta(days=new_days)
        new_items = [v for v in videos if v.created_at >= cutoff]
        started = [v for v in videos if v.progress_id is not None]

        grouped = defaultdict(list)
        for v in videos:
            grouped[v.genre].append(v)

        payload = []
        if new_items:
            s = VideoListItemSerializer(new_items, many=True,
                                        context={"request": request})
            payload.append({"genre": "New on Videoflix", "videos": s.data})
        if started:
            s = VideoListItemSerializer(started, many=True,
                                        context={"request": request})
            payload.append({"genre": "Started videos", "videos": s.data})
        for genre in sorted(grouped.keys()):
            s = VideoListItemSerializer(grouped[genre], many=True,
                                        context={"request": request})
            payload.append({"genre": genre, "videos": s.data})
        return Response(payload)


class VideoDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        vp = VideoProgress.objects.filter(
            user_id=request.user.id, video_id=OuterRef("pk")
        )
        video = (Video.objects.filter(pk=pk)
                 .annotate(progress_id=Subquery(vp.values("id")[:1]),
                           last_position=Subquery(
                               vp.values("last_position")[:1]))
                 .first())
        if not video:
            return Response({"detail": "Not found."}, status=404)
        ser = VideoDetailSerializer(video, context={"request": request})
        return Response({"video": ser.data})
