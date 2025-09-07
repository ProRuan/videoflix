# Standard libraries

# Third-party suppliers
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from auth_app.api.serializers import (
    AccountActivationSerializer,
    AccountDeletionSerializer,
    AccountReactivationSerializer,
    DeregistrationSerializer,
    EmailCheckSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordResetRequestSerializer,
    PasswordUpdateSerializer,
    RegistrationSerializer
)


class RegistrationView(APIView):
    """POST /api/registration/ -> { email, user_id }."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegistrationSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        user = ser.save()
        return Response({"email": user.email, "user_id": user.id},
                        status=status.HTTP_201_CREATED)


class AccountActivationView(APIView):
    """POST /api/account-activation/ -> { email, user_id }."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = AccountActivationSerializer(data=request.data)
        if not ser.is_valid():
            msg = ser.errors.get("token", [""])[0]
            if "Token not found" in str(msg):
                return Response({"detail": "Token not found."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": str(msg)},
                            status=status.HTTP_400_BAD_REQUEST)
        user = ser.save()
        return Response(ser.to_representation(user), status=status.HTTP_200_OK)


class AccountReactivationView(APIView):
    """POST /api/account-reactivation/ -> { email, user_id }."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = AccountReactivationSerializer(data=request.data)
        if not ser.is_valid():
            msg = ser.errors.get("email", [""])[0]
            if "User not found" in str(msg):
                return Response({"detail": "User not found."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": str(msg)},
                            status=status.HTTP_400_BAD_REQUEST)
        user = ser.save()
        return Response(ser.to_representation(user), status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    """POST /api/email-check/ -> { email, exists }."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = EmailCheckSerializer(data=request.data)
        if not ser.is_valid():
            return Response({"detail": str(ser.errors.get("email", [""])[0])},
                            status=status.HTTP_400_BAD_REQUEST)
        data = ser.save()
        return Response(data, status=status.HTTP_200_OK)


class LoginView(APIView):
    """POST /api/login/ -> { token, email, user_id }."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            return Response({"detail": str(ser.errors.get("__all__", [
                ser.errors.get("email", [""])[0] or
                ser.errors.get("password", [""])[0]
            ])[0])}, status=status.HTTP_400_BAD_REQUEST)
        data = ser.save()
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """POST /api/logout/ -> { email, user_id }."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LogoutSerializer(data=request.data)
        if not ser.is_valid():
            msg = ser.errors.get("token", [""])[0]
            if "Token not found" in str(msg):
                return Response({"detail": "Token not found."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": str(msg)},
                            status=status.HTTP_400_BAD_REQUEST)
        data = ser.save()
        return Response(data, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """POST /api/password-reset/ -> { email }."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = PasswordResetRequestSerializer(data=request.data)
        if not ser.is_valid():
            msg = ser.errors.get("email", [""])[0]
            if "User not found" in str(msg):
                return Response({"detail": "User not found."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": str(msg)},
                            status=status.HTTP_400_BAD_REQUEST)
        data = ser.save()
        return Response(data, status=status.HTTP_200_OK)


class PasswordUpdateView(APIView):
    """POST /api/password-update/ -> { email, user_id }."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = PasswordUpdateSerializer(data=request.data)
        if not ser.is_valid():
            msg = ser.errors.get("token") or ser.errors.get("email") \
                or ser.errors.get("__all__") or ["Invalid data."]
            text = str(msg[0])
            if "Token not found" in text:
                return Response({"detail": "Token not found."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": text},
                            status=status.HTTP_400_BAD_REQUEST)
        data = ser.save()
        return Response(data, status=status.HTTP_200_OK)


class DeregistrationView(APIView):
    """POST /api/deregistration/ -> { email, user_id }."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = DeregistrationSerializer(data=request.data)
        if not ser.is_valid():
            msg = (ser.errors.get("token") or ser.errors.get("email") or
                   ser.errors.get("password") or ser.errors.get("__all__") or
                   ["Invalid data."])
            text = str(msg[0])
            if "Token not found" in text:
                return Response({"detail": "Token not found."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": text},
                            status=status.HTTP_400_BAD_REQUEST)
        data = ser.save()
        return Response(data, status=status.HTTP_200_OK)


class AccountDeletionView(APIView):
    """POST /api/account-deletion/ -> 204 No Content."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = AccountDeletionSerializer(data=request.data)
        if not ser.is_valid():
            msg = ser.errors.get("token", [""])[0]
            if "Token not found" in str(msg):
                return Response({"detail": "Token not found."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": str(msg)},
                            status=status.HTTP_400_BAD_REQUEST)
        ser.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
