# # video_offer_app/views.py

# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework import viewsets, status
# import os
# from django.conf import settings
# from .models import Video
# from .serializers import VideoSerializer

# class VideoViewSet(viewsets.ModelViewSet):
#     queryset = Video.objects.all()
#     serializer_class = VideoSerializer

#     @action(detail=True, url_path='hls/(?P<res>[^/.]+)')
#     def hls_variant(self, request, pk=None, res=None):
#         """
#         GET /videos/{pk}/hls/720p/  →  returns the URL of the 720p variant playlist
#         """
#         vid = self.get_object()
#         if res not in vid.available_resolutions:
#             return Response(
#                 {'detail': f'Resolution {res} not available.'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         # build the URL
#         rel = vid.hls_playlist.name  # e.g. videos/hls/<base>/<base>.m3u8
#         base_dir = os.path.dirname(rel)
#         variant_path = os.path.join(base_dir, res, 'index.m3u8')
#         return Response({
#             'url': request.build_absolute_uri(settings.MEDIA_URL + variant_path)
#         })


# views.py
from .permissions import IsAdminOrReadOnly
# from .models import Video
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics, viewsets
from rest_framework import status, authentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from video_offer_app.models import Video, VideoProgress
from .serializers import VideoSerializer, VideoProgressSerializer


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


class VideoDetailView(APIView):
    """
    GET    → 200, 401 (if auth required), 404 (if not found)
    PATCH  → 200, 400, 401, 404
    DELETE → 204, 401, 403, 404
    """
    permission_classes = [AllowAny]

    # Support both session- and token-based auth so client.login() works
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        serializer = VideoSerializer(video)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        # 401 if unauthenticated
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # 403 if not staff
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        video = get_object_or_404(Video, pk=pk)
        serializer = VideoSerializer(video, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # 401 if unauthenticated
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # 403 if not staff
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        video = get_object_or_404(Video, pk=pk)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class VideoProgressViewSet(viewsets.ModelViewSet):
#     """
#     list:    Not needed (you’ll filter by video/user)
#     retrieve: GET /progress/{pk}/
#     create:   POST /progress/  (video + last_position)
#     update:   PATCH /progress/{pk}/
#     """
#     queryset = VideoProgress.objects.all()
#     serializer_class = VideoProgressSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         # Users can only see their own progress
#         return self.queryset.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         # Attach current user
#         serializer.save(user=self.request.user)

#     def perform_update(self, serializer):
#         # Prevent updating someone else’s
#         if serializer.instance.user != self.request.user:
#             raise PermissionDenied("Cannot update another user’s progress")
#         serializer.save()

class VideoProgressListCreate(generics.ListCreateAPIView):
    """
    GET  /api/progress/?video=<id>   → list (filtered by video & user)
    POST /api/progress/              → upsert-or-delete progress
    """
    serializer_class = VideoProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = VideoProgress.objects.filter(user=self.request.user)
        video_id = self.request.query_params.get('video')
        if video_id:
            qs = qs.filter(video_id=video_id)
        return qs

    def create(self, request, *args, **kwargs):
        # Expect payload: { "video": 123, "last_position": N }
        vid_id = request.data.get('video')
        pos = int(request.data.get('last_position', 0))
        try:
            video = Video.objects.get(pk=vid_id)
        except Video.DoesNotExist:
            return Response({'detail': 'Video not found.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # If in-progress, upsert; otherwise delete any existing and 204
        if 0 < pos < (video.duration or 0):
            obj, created = VideoProgress.objects.update_or_create(
                user=request.user, video=video,
                defaults={'last_position': pos}
            )
            serializer = self.get_serializer(obj)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        # not started or finished → remove any progress
        VideoProgress.objects.filter(user=request.user, video=video).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoProgressRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = VideoProgress.objects.all()
    serializer_class = VideoProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.user_id != self.request.user.id:
            raise PermissionDenied("Cannot access another user’s progress")
        return obj

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        pos = int(request.data.get('last_position', 0))
        duration = instance.video.duration or 0

        # Only update if in-progress
        if 0 < pos < duration:
            instance.last_position = pos
            instance.save(update_fields=['last_position'])
            return Response(self.get_serializer(instance).data)
        # Otherwise do nothing here (frontend should call DELETE)
        return Response(status=status.HTTP_204_NO_CONTENT)

# class VideoProgressRetrieveUpdate(generics.RetrieveUpdateAPIView):
#     """
#     GET   /api/progress/<pk>/   → retrieve single record
#     PATCH /api/progress/<pk>/   → update or delete progress
#     """
#     queryset = VideoProgress.objects.all()
#     serializer_class = VideoProgressSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         obj = super().get_object()
#         if obj.user_id != self.request.user.id:
#             raise PermissionDenied("Cannot access another user’s progress")
#         return obj

#     def patch(self, request, *args, **kwargs):
#         instance = self.get_object()
#         pos = int(request.data.get('last_position', 0))
#         duration = instance.video.duration or 0

#         # In‑progress → update; else → delete + 204
#         if 0 < pos < duration:
#             instance.last_position = pos
#             instance.save(update_fields=['last_position'])
#             serializer = self.get_serializer(instance)
#             return Response(serializer.data)
#         else:
#             instance.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
