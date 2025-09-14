# Third-party suppliers
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from ..models import VideoProgress
from .permissions import IsOwner
from .serializers import (VideoProgressCreateSerializer,
                          VideoProgressDetailSerializer)


class VideoProgressCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = VideoProgressCreateSerializer(data=request.data,
                                            context={"request": request})
        if not ser.is_valid():
            if ser.errors.get("video_id") == ["Video not found."]:
                return Response({"detail": "Not found."}, status=404)
            return Response(ser.errors, status=400)
        obj = ser.save()
        return Response(VideoProgressDetailSerializer(obj).data, status=201)


class VideoProgressDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]

    def _get_obj(self, pk):
        try:
            return (VideoProgress.objects
                    .select_related("user", "video").get(pk=pk))
        except VideoProgress.DoesNotExist:
            return None

    def patch(self, request, pk: int):
        obj = self._get_obj(pk)
        if not obj:
            return Response({"detail": "Not found."}, status=404)
        self.check_object_permissions(request, obj)
        last = request.data.get("last_position")
        try:
            last = float(last)
        except (TypeError, ValueError):
            return Response({"last_position": ["This field is invalid."]},
                            status=400)
        if last < 0:
            return Response({"last_position": ["This field is invalid."]},
                            status=400)
        dur = obj.video.duration or 0.0
        obj.last_position = last
        obj.relative_position = round(last / dur * 100, 2) if dur > 0 else 0.0
        obj.save(update_fields=["last_position", "relative_position"])
        return Response(VideoProgressDetailSerializer(obj).data)

    def delete(self, request, pk: int):
        obj = self._get_obj(pk)
        if not obj:
            return Response({"detail": "Not found."}, status=404)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=204)
