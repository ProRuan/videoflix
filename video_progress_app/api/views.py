# Third-party suppliers
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from video_progress_app.models import VideoProgress
from .permissions import IsOwner
from .serializers import (
    VideoProgressCreateSerializer,
    VideoProgressDetailSerializer,
    VideoProgressUpdateSerializer,
)


class VideoProgressCreateView(APIView):
    """
    Class representing a video progress create view.

    Post a video progress for specific user and video.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Post video progress."""
        ser = VideoProgressCreateSerializer(data=request.data,
                                            context={"request": request})
        if not ser.is_valid():
            if ser.errors.get("video_id") == ["Video not found."]:
                return Response({"detail": "Not found."}, status=404)
            return Response(ser.errors, status=400)
        obj = ser.save()
        return Response(VideoProgressDetailSerializer(obj).data, status=201)


class VideoProgressDetailView(APIView):
    """
    Class representing a video progress detail view.

    Patches and deletes video progress.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]

    def _get_obj(self, pk):
        """Get video progress for specific user and video."""
        try:
            return (VideoProgress.objects
                    .select_related("user", "video").get(pk=pk))
        except VideoProgress.DoesNotExist:
            return None

    def patch(self, request, pk: int):
        """Patch video progress."""
        obj = self._get_obj(pk)
        if not obj:
            return Response({"detail": "Not found."}, status=404)
        self.check_object_permissions(request, obj)
        ser = VideoProgressUpdateSerializer(obj, data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=400)
        ser.save()
        return Response(VideoProgressDetailSerializer(obj).data)

    def delete(self, request, pk: int):
        """Delete video progress."""
        obj = self._get_obj(pk)
        if not obj:
            return Response({"detail": "Not found."}, status=404)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=204)
