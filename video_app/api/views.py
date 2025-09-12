# Standard libraries
from datetime import timedelta

# Third-party suppliers
from django.utils import timezone
from knox.auth import TokenAuthentication
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from ..models import Video
from .serializers import VideoItemSerializer


class VideoListView(APIView):
    """Return [{genre, videos}] with 'New...' first; sorted."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recent = timezone.now() - timedelta(days=90)
        qs = Video.objects.all().order_by("-created_at", "title")
        new_qs = qs.filter(created_at__gte=recent)
        ctx = {"request": request}
        buckets = [{
            "genre": "New on Videoflix",
            "videos": VideoItemSerializer(new_qs, many=True,
                                          context=ctx).data,
        }]
        by_genre = {}
        for v in qs:
            by_genre.setdefault(v.genre, []).append(v)
        for genre in sorted(by_genre):
            data = VideoItemSerializer(by_genre[genre], many=True,
                                       context=ctx).data
            buckets.append({"genre": genre, "videos": data})
        return Response(buckets)


class VideoDetailView(RetrieveAPIView):
    """Return a single video by id."""
    queryset = Video.objects.all()
    serializer_class = VideoItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
