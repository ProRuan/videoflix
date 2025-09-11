# auth_app/api/views.py
# Standard libraries
from datetime import timedelta

# Third-party suppliers
from django.contrib.auth import authenticate, get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from knox.auth import TokenAuthentication

# Local imports
from auth_app.api.serializers import (
    AccountActivationSerializer,
    AccountDeletionSerializer,
    AccountReactivationSerializer,
    DeregistrationSerializer,
    PasswordUpdateSerializer,
    RegistrationSerializer,
)
from auth_app.utils import (
    build_activation_link,
    build_deletion_link,
    build_reset_link,
    create_knox_token,
    resolve_knox_token,
    send_activation_email,
    send_deletion_email,
    send_reset_email,
    validate_email_or_raise,
    validate_email_unique,
)

User = get_user_model()


def _bad(detail: str) -> Response:
    """Return a uniform 400 response with detail list."""
    return Response({"detail": [detail]}, status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(APIView):
    """Create inactive user, issue 24h token, send activation email."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = RegistrationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        token = create_knox_token(user, hours=24)
        link = build_activation_link(token)
        send_activation_email(user, link)
        data = {"email": user.email, "user_id": user.id, "is_active": False}
        return Response(data, status=status.HTTP_201_CREATED)


class AccountActivationView(APIView):
    """Activate user by body token; delete that Knox token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
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
    """Send activation mail if user exists; always 200 on valid email."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = AccountReactivationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if user:
            token = create_knox_token(user, hours=24)
            send_activation_email(user, build_activation_link(token))
        return Response({"email": email}, status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    """Check email is syntactically valid and not yet registered."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data or {}).get("email", "")
        try:
            validate_email_or_raise(email)
            validate_email_unique(email)
        except Exception:
            return _bad("Please check your email and try again.")
        return Response({"email": email}, status=status.HTTP_200_OK)


class LoginView(APIView):
    """Authenticate by email/password and issue a 12h Knox token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data or {}
        email = data.get("email", "")
        password = data.get("password", "")
        if not email or not password:
            return _bad("Please check your login data and try again.")
        user = authenticate(request, email=email, password=password)
        if not user:
            return _bad("Please check your login data and try again.")
        token = create_knox_token(user, hours=12)
        out = {"email": user.email, "user_id": user.id, "token": token}
        return Response(out, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Delete the current Knox token to log the user out."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if hasattr(request.auth, "delete"):
            request.auth.delete()
        msg = {"message": ["Logout successful."]}
        return Response(msg, status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    """Send reset email if user exists; 200 for valid emails else 400."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data or {}).get("email", "")
        try:
            validate_email_or_raise(email)
        except Exception:
            return _bad("Please check your email and try again.")
        user = User.objects.filter(email__iexact=email).first()
        if user:
            token = create_knox_token(user, hours=1)
            send_reset_email(email, build_reset_link(token))
        return Response({"email": email}, status=status.HTTP_200_OK)


class PasswordUpdateView(APIView):
    """Update password for authed user; delete current Knox token."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = PasswordUpdateSerializer(data=request.data)
        if not ser.is_valid():
            return _bad("Please check your input and try again.")
        if request.user.email != ser.validated_data["email"]:
            return _bad("Please check your input and try again.")
        user = request.user
        user.set_password(ser.validated_data["password"])
        user.save(update_fields=["password"])
        if hasattr(request.auth, "delete"):
            request.auth.delete()
        out = {"email": user.email, "user_id": user.id}
        return Response(out, status=status.HTTP_200_OK)


class DeregistrationView(APIView):
    """Re-auth user, email 24h deletion link; header Knox auth."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = DeregistrationSerializer(data=request.data)
        if not ser.is_valid():
            return _bad("Please check your input and try again.")
        email = ser.validated_data["email"]
        if email != request.user.email:
            return _bad("Please check your input and try again.")
        authed = authenticate(
            request, email=email, password=ser.validated_data["password"]
        )
        if not authed or authed.pk != request.user.pk:
            return _bad("Please check your input and try again.")
        token = create_knox_token(request.user, hours=24)
        send_deletion_email(request.user, build_deletion_link(token))
        return Response({"email": email}, status=status.HTTP_200_OK)


class AccountDeletionView(APIView):
    """Delete account; requires a valid deletion token in Authorization."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        if hasattr(request.auth, "delete"):
            request.auth.delete()
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
