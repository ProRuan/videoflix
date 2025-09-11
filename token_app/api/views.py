# Standard libraries

# Third-party suppliers
from knox.auth import TokenAuthentication as KnoxAuth
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

# Local imports
from token_app.api.serializers import ActivationTokenCheckSerializer
from token_app.utils import resolve_knox_token


class ActivationTokenCheckView(APIView):
    """Check activation token; return token, email and user_id."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = ActivationTokenCheckSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            obj = resolve_knox_token(ser.validated_data["token"])
        except ValidationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        u = obj.user
        data = {"token": ser.validated_data["token"],
                "email": u.email, "user_id": u.id}
        return Response(data, status=status.HTTP_200_OK)


class TokenCheckView(APIView):
    """Verify Knox token and return token, email and user_id."""
    authentication_classes = [KnoxAuth]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        token = auth.split(" ", 1)[1] if auth.startswith("Token ") else ""
        data = {"token": token, "email": request.user.email,
                "user_id": request.user.id}
        return Response(data, status=status.HTTP_200_OK)
