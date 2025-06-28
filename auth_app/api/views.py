# Third-party suppliers
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    RegistrationSerializer,
    ResetPasswordSerializer,
)
from auth_app.utils import (
    build_auth_response,
    send_confirm_email_email,
    send_reset_password_email,
    validate_serializer_or_400,
)

User = get_user_model()


class RegistrationView(APIView):
    """
    Represents a registration view.
        - POST creates a new user and triggers a confirm-email email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Post user registration data.
        Triggers a confirm-email email.
        Returns token, email and user_id.
        """
        serializer = RegistrationSerializer(data=request.data)
        error = validate_serializer_or_400(serializer)
        if error:
            return error
        user = serializer.save()
        view_payload, view_status = build_auth_response(
            user, status.HTTP_201_CREATED)
        activation_link = f"https://your-frontend.com/activate?token={view_payload['token']}"
        send_confirm_email_email(user, activation_link)
        return Response(view_payload, status=view_status)


class LoginView(APIView):
    """
    Represents a login view.
        - POST authenticates a user.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Post user login data.
        Returns token, email and user_id.
        """
        serializer = LoginSerializer(data=request.data)
        error = validate_serializer_or_400(serializer)
        if error:
            return error
        user = serializer.validated_data['user']
        view_payload, view_status = build_auth_response(
            user, status.HTTP_200_OK)
        return Response(view_payload, status=view_status)


class ForgotPasswordView(APIView):
    """
    Represents a forgot-password view.
        - POST triggers a reset-password email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Post user email.
        Triggers a reset-password email.
        Returns token, email and user_id.
        """
        serializer = ForgotPasswordSerializer(data=request.data)
        error = validate_serializer_or_400(serializer)
        if error:
            return error
        user = User.objects.get(email=serializer.validated_data['email'])
        view_payload, view_status = build_auth_response(
            user, status.HTTP_200_OK)
        reset_link = f"https://your-frontend.com/reset-password?token={view_payload['token']}"
        send_reset_password_email(user, reset_link)
        return Response(view_payload, status=view_status)


class ResetPasswordView(APIView):
    """
    Represents a reset-password view.
        - POST updates a user´s password.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Post new passwords.
        Returns token, email and user_id.
        """
        serializer = ResetPasswordSerializer(data=request.data)
        error = validate_serializer_or_400(serializer)
        if error:
            return error
        token = serializer.save()
        user = token.user
        return Response(
            {'token': token.key, 'email': user.email, 'user_id': user.id},
            status=status.HTTP_200_OK
        )
