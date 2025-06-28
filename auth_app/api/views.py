# Third-party suppliers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from .serializers import (
    ForgotPasswordSerializer, LoginSerializer,
    RegistrationSerializer, ResetPasswordSerializer,
)
from auth_app.utils import (
    build_auth_response,
    validate_serializer_or_400,
)

User = get_user_model()


class RegistrationView(APIView):
    """
    Represents a registration view.
        - POST creates new user and triggers confirm-email email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Post user registration data.
        Triggers confirm-email email.
        Returns token, email and user_id.
        """
        serializer = RegistrationSerializer(data=request.data)
        error = validate_serializer_or_400(serializer)
        if error:
            return error
        user = serializer.save()

        send_mail(
            'Welcome to Videoflix',
            'Thank you for registering. Your account is ready to use.',
            'no-reply@videoflix.com',
            [user.email],
            fail_silently=True,
        )

        view_payload, view_status = build_auth_response(
            user, status.HTTP_201_CREATED)
        return Response(view_payload, status=view_status)


class LoginView(APIView):
    """
    Represents a login view.
        - POST authenticates user.
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
        - POST triggers reset-password email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Post user email.
        Triggers reset-password email.
        Returns token, email and user_id.
        """
        serializer = ForgotPasswordSerializer(data=request.data)
        error = validate_serializer_or_400(serializer)
        if error:
            return error
        user = User.objects.get(email=serializer.validated_data['email'])
        view_payload, view_status = build_auth_response(
            user, status.HTTP_200_OK)

        send_mail(
            'Reset your Videoflix password',
            f'Use this token to reset your password: {view_payload['token']}',
            'no-reply@videoflix.com',
            [user.email],
            fail_silently=True,
        )

        return Response(view_payload, status=view_status)


class ResetPasswordView(APIView):
    """
    Represents a reset-password view.
        - POST updates user password.
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
