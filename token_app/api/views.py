from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..utils import (
    create_token_for_user,
    get_token_and_type_by_value,
    token_expired,
    token_expiry_datetime,
    TOKEN_MAP,
)
from .serializers import (
    TokenCreationSerializer,
    TokenCreationResponseSerializer,
    TokenCheckSerializer,
    TokenCheckResponseSerializer,
)

User = get_user_model()


class TokenCreationView(APIView):
    """
    POST /api/token/creation/
    Body: { user: <id>, type: "activation"|"deletion"|"password_reset" }
    Status codes:
      200 - token creation successful
      400 - bad request (missing/invalid fields)
      404 - user not found
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data or {}
        # quick presence checks to match required status codes
        if "user" not in data or "type" not in data:
            return Response({"detail": "user and type are required."}, status=status.HTTP_400_BAD_REQUEST)
        user_pk = data.get("user")
        token_type = data.get("type")
        if token_type not in TOKEN_MAP:
            return Response({"detail": "invalid token type."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response({"detail": "user not found."}, status=status.HTTP_404_NOT_FOUND)

        instance = create_token_for_user(user, token_type)
        payload = {
            "token": instance.token,
            "type": token_type,
            "user": user.pk,
            "lifetime": instance.lifetime,
            "created_at": instance.created_at,
            "expired_at": token_expiry_datetime(instance),
        }
        out = TokenCreationResponseSerializer(payload)
        return Response(out.data, status=status.HTTP_200_OK)


class TokenCheckView(APIView):
    """
    POST /api/token/check/
    Body: { token } or { token, used: true }
    Status codes:
      200 - token check successful
      400 - bad request (missing, invalid, used or expired)
      404 - token not found
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data or {}
        token_value = data.get("token")
        if not token_value:
            return Response({"detail": "token is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance, type_str = get_token_and_type_by_value(token_value)
        if not instance:
            return Response({"detail": "token not found."}, status=status.HTTP_404_NOT_FOUND)

        # If request wants to mark used
        if "used" in data:
            # we only accept setting used=True per spec
            if not bool(data.get("used")):
                return Response({"detail": "invalid used value."}, status=status.HTTP_400_BAD_REQUEST)
            # can't mark used if expired or already used
            if token_expired(instance):
                return Response({"detail": "token expired."}, status=status.HTTP_400_BAD_REQUEST)
            if instance.used:
                return Response({"detail": "token already used."}, status=status.HTTP_400_BAD_REQUEST)
            instance.used = True
            instance.save(update_fields=["used"])
            payload = {"token": instance.token, "type": type_str,
                       "user": instance.user.pk, "used": True}
            out = TokenCheckResponseSerializer(payload)
            return Response(out.data, status=status.HTTP_200_OK)

        # just checking token validity
        if token_expired(instance):
            return Response({"detail": "token expired."}, status=status.HTTP_400_BAD_REQUEST)
        if instance.used:
            return Response({"detail": "token already used."}, status=status.HTTP_400_BAD_REQUEST)

        payload = {"token": instance.token, "type": type_str,
                   "user": instance.user.pk, "email": instance.user.email, "used": instance.used}
        out = TokenCheckResponseSerializer(payload)
        return Response(out.data, status=status.HTTP_200_OK)
