# Third-party suppliers
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from video_app.models import Video
from video_app.utils import (
    annotate_detail_with_progress,
    annotate_with_progress
)
from video_app.utils import build_list_payload
from .serializers import VideoDetailSerializer


class VideoListView(APIView):
    """
    Class representing a video list view.

    List video items sorted by genre. Videos are sorted by created_at.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get video list."""
        qs = Video.objects.all().order_by("-created_at", "title")
        qs = annotate_with_progress(qs, request.user.id)
        payload = build_list_payload(list(qs), request)
        return Response(payload)


class VideoDetailView(APIView):
    """
    Class representing a video detail view.

    Retrieve video with all details.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        """Get video detail."""
        qs = annotate_detail_with_progress(Video.objects.filter(pk=pk),
                                           request.user.id)
        video = qs.first()
        if not video:
            return Response({"detail": "Not found."}, status=404)
        ser = VideoDetailSerializer(video, context={"request": request})
        return Response({"video": ser.data})
