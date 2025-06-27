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
        if not serializer.is_valid():
            return Response(
                {'detail': 'Please check your data and try it again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        send_mail(
            'Welcome to Videoflix',
            'Thank you for registering. Your account is ready to use.',
            'no-reply@videoflix.com',
            [user.email],
            fail_silently=True,
        )

        return Response(
            {'token': token.key, 'email': user.email, 'user_id': user.id},
            status=status.HTTP_201_CREATED
        )


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
        if not serializer.is_valid():
            return Response(
                {'detail': 'Please check your data and try it again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'token': token.key, 'email': user.email, 'user_id': user.id},
            status=status.HTTP_200_OK
        )


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
        if not serializer.is_valid():
            return Response(
                {'detail': 'Please check your data and try it again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.get(email=serializer.validated_data['email'])
        token, _ = Token.objects.get_or_create(user=user)

        send_mail(
            'Reset your Videoflix password',
            f'Use this token to reset your password: {token.key}',
            'no-reply@videoflix.com',
            [user.email],
            fail_silently=True,
        )

        return Response(
            {'token': token.key, 'email': user.email, 'user_id': user.id},
            status=status.HTTP_200_OK
        )


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
        if not serializer.is_valid():
            return Response(
                {'detail': 'Please check your data and try it again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        token = serializer.save()
        user = token.user
        return Response(
            {'token': token.key, 'email': user.email, 'user_id': user.id},
            status=status.HTTP_200_OK
        )
