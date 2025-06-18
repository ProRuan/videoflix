# views.py
from rest_framework import status, authentication
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from video_offer_app.models import Video
from .serializers import VideoSerializer


class VideoListCreateView(ListCreateAPIView):
    """
    GET  /api/videos/ → 200 or 400 on unexpected query params
    POST /api/videos/ → 401, 403, 400 or 201
    """
    queryset = Video.objects.all().order_by('-created_at')
    serializer_class = VideoSerializer

    # allow both session- and token-auth so `client.login()` works in tests
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]
    # open GET to everyone
    permission_classes = []  # we’ll enforce POST auth manually

    parser_classes = [MultiPartParser, FormParser]

    def list(self, request, *args, **kwargs):
        # reject any unexpected query params
        if request.query_params and any(
            key not in ()  # no allowed filters
            for key in request.query_params
        ):
            return Response(
                {"detail": "Invalid query parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # 401 if not logged in
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # 403 if logged in but not staff
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        # delegate payload validation and saving to DRF
        return super().create(request, *args, **kwargs)
