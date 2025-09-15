# Third-party suppliers
from django.contrib.auth import authenticate, get_user_model
from knox.auth import TokenAuthentication
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from auth_app.api.serializers import (
    AccountActivationSerializer,
    AccountReactivationSerializer,
    DeregistrationSerializer,
    PasswordUpdateSerializer,
    RegistrationSerializer,
)
from auth_app.utils import (
    ACTIVATION_TTL_H,
    build_activation_link,
    build_deletion_link,
    build_reset_link,
    create_knox_token,
    DELETION_TTL_H,
    LOGIN_TTL_H,
    REACTIVATION_TTL_H,
    reauthenticate,
    RESET_TTL_H,
    resolve_knox_token,
    send_activation_email,
    send_deletion_email,
    send_reset_email,
    validate_email_or_raise,
    validate_email_unique,
)

User = get_user_model()
BAD = "Please check your input and try again."
BAD_EMAIL = "Please check your email and try again."
BAD_LOGIN = "Please check your login data and try again."


def _bad(detail: str) -> Response:
    """Return a uniform 400 response with detail list."""
    return Response({"detail": [detail]}, status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(APIView):
    """
    Class representing a registration view.

    Creates an inactive user and sends an activation email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Post registration data and perform registration."""
        ser = RegistrationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        token = create_knox_token(user, hours=ACTIVATION_TTL_H)
        send_activation_email(user, build_activation_link(token))
        data = {"email": user.email, "user_id": user.id, "is_active": False}
        return Response(data, status=status.HTTP_201_CREATED)


class AccountActivationView(APIView):
    """
    Class representing an account activation view.

    Activates a user by account activation token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Post account activation token and perform account activation."""
        ser = AccountActivationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = resolve_knox_token(ser.validated_data["token"])
        if obj is None:
            return Response({"detail": "Not found."}, status=404)
        user = obj.user
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
        obj.delete()
        data = {"email": user.email, "user_id": user.id, "is_active": True}
        return Response(data, status=status.HTTP_200_OK)


class AccountReactivationView(APIView):
    """
    Class representing an account reactivation view.

    Resends account activation email, if user exists.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Post email and perform account reactivation."""
        ser = AccountReactivationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if user:
            token = create_knox_token(user, hours=REACTIVATION_TTL_H)
            send_activation_email(user, build_activation_link(token))
        return Response({"email": email}, status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    """
    Class representing an email check view.

    Check email for validity and non-registered status.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Post email and perform email check."""
        email = (request.data or {}).get("email", "")
        try:
            validate_email_or_raise(email)
            validate_email_unique(email)
        except Exception:
            return _bad(BAD_EMAIL)
        return Response({"email": email}, status=status.HTTP_200_OK)


class LoginView(APIView):
    """
    Class representing a login view.

    Authenticates a user by email and password.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Post email and password and perform login."""
        data = request.data or {}
        email, password = data.get("email", ""), data.get("password", "")
        if not email or not password:
            return _bad(BAD_LOGIN)
        user = authenticate(request, email=email, password=password)
        if not user:
            return _bad(BAD_LOGIN)
        token = create_knox_token(user, hours=LOGIN_TTL_H)
        out = {"email": user.email, "user_id": user.id, "token": token}
        return Response(out, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Class representing a logout view.

    Deletes the auth token to log the user out.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Post auth token via headers and perform logout."""
        if hasattr(request.auth, "delete"):
            request.auth.delete()
        return Response({"message": ["Logout successful."]}, status=200)


class PasswordResetView(APIView):
    """
    Class representing a password reset view.

    Validates email and sends password reset email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Post email and perform password reset."""
        email = (request.data or {}).get("email", "")
        try:
            validate_email_or_raise(email)
        except Exception:
            return _bad(BAD_EMAIL)
        user = User.objects.filter(email__iexact=email).first()
        if user:
            token = create_knox_token(user, hours=RESET_TTL_H)
            send_reset_email(email, build_reset_link(token))
        return Response({"email": email}, status=status.HTTP_200_OK)


class PasswordUpdateView(APIView):
    """
    Class representing a password update view.

    Updates the user´s password.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Post email and passwords and perform password update."""
        ser = PasswordUpdateSerializer(data=request.data)
        if not ser.is_valid():
            return _bad(BAD)
        if request.user.email != ser.validated_data["email"]:
            return _bad(BAD)
        user = request.user
        user.set_password(ser.validated_data["password"])
        user.save(update_fields=["password"])
        if hasattr(request.auth, "delete"):
            request.auth.delete()
        out = {"email": user.email, "user_id": user.id}
        return Response(out, status=status.HTTP_200_OK)


class DeregistrationView(APIView):
    """
    Class representing a deregistration view.

    Reauthenticates a user and sends an account deletion email.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Post email and password and perform deregistration."""
        ser = DeregistrationSerializer(data=request.data)
        if not ser.is_valid():
            return _bad(BAD)
        email = ser.validated_data["email"]
        if email != request.user.email:
            return _bad(BAD)
        user = reauthenticate(request, email, ser.validated_data["password"])
        if not user or user.pk != request.user.pk:
            return _bad(BAD)
        token = create_knox_token(request.user, hours=DELETION_TTL_H)
        send_deletion_email(request.user, build_deletion_link(token))
        return Response({"email": email}, status=status.HTTP_200_OK)


class AccountDeletionView(APIView):
    """
    Class representing an account deletion view.

    Deletes a user´s account.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """Deletes a user´s account."""
        if hasattr(request.auth, "delete"):
            request.auth.delete()
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
