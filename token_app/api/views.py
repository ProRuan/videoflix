from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..utils import (
    create_token_for_user,
    get_token_instance_by_value,
    token_expiry_datetime,
)
from .serializers import (
    TokenCreationSerializer,
    TokenCreationResponseSerializer,
    TokenCheckSerializer,
    TokenCheckResponseSerializer,
)


class TokenCreationView(APIView):
    """
    POST /api/token/creation/
    Body: { user: <id>, type: "activation"|"deletion"|"password_reset" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token_type = serializer.validated_data["type"]
        instance = create_token_for_user(user, token_type)
        payload = {
            "token": instance.token,
            "user": user.pk,
            "lifetime": instance.lifetime,
            "created_at": instance.created_at,
            "expired_at": token_expiry_datetime(instance),
        }
        out = TokenCreationResponseSerializer(payload)
        return Response(out.data, status=status.HTTP_201_CREATED)


class TokenCheckView(APIView):
    """
    POST /api/token/check/
    Body: { token: "<hex>" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_value = serializer.validated_data["token"]
        instance = get_token_instance_by_value(token_value)
        if not instance:
            return Response(
                {"detail": "Token not found."}, status=status.HTTP_404_NOT_FOUND
            )
        payload = {"token": instance.token,
                   "user": instance.user.pk, "used": instance.used}
        out = TokenCheckResponseSerializer(payload)
        return Response(out.data, status=status.HTTP_200_OK)
