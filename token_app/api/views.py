# Third-party suppliers
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from token_app.api.serializers import TokenCheckSerializer


class TokenCheckView(APIView):
    """POST /api/token/check/ -> { token, email, user_id }."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = TokenCheckSerializer(data=request.data)
        if not ser.is_valid():
            msg = ser.errors.get("token", [""])[0]
            text = str(msg)
            if "Token not found" in text:
                return Response({"detail": "Token not found."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": text},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(ser.data, status=status.HTTP_200_OK)
