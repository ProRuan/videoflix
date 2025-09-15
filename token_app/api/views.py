# Third-party suppliers
from knox.auth import TokenAuthentication as KnoxAuth
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

# Local imports
from token_app.api.serializers import ActivationTokenCheckSerializer
from token_app.utils import resolve_knox_token


class ActivationTokenCheckView(APIView):
    """
    Class representing an activation token check serializer.

    Validates an account activation token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Post an activation token and perform activation token check."""
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
    """
    Class representing a token check view.

    Validates a token.
    """
    authentication_classes = [KnoxAuth]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Post a token and perform token check."""
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        token = auth.split(" ", 1)[1] if auth.startswith("Token ") else ""
        data = {"token": token, "email": request.user.email,
                "user_id": request.user.id}
        return Response(data, status=status.HTTP_200_OK)
