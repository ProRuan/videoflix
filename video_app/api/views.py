# Standard libraries

# Third-party suppliers
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from ..models import Video
from ..utils import annotate_detail_with_progress, annotate_with_progress
from ..utils import build_list_payload
from .serializers import VideoDetailSerializer


class VideoListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Video.objects.all().order_by("-created_at", "title")
        qs = annotate_with_progress(qs, request.user.id)
        payload = build_list_payload(list(qs), request)
        return Response(payload)


class VideoDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        qs = annotate_detail_with_progress(Video.objects.filter(pk=pk),
                                           request.user.id)
        video = qs.first()
        if not video:
            return Response({"detail": "Not found."}, status=404)
        ser = VideoDetailSerializer(video, context={"request": request})
        return Response({"video": ser.data})
