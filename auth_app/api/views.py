# Standard libraries
from datetime import timedelta

# Third-party suppliers
from django.contrib.auth import authenticate, get_user_model
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from knox.auth import TokenAuthentication

# Local imports
from auth_app.api.serializers import AccountActivationSerializer, AccountDeletionSerializer, AccountReactivationSerializer, DeregistrationSerializer, PasswordUpdateSerializer, RegistrationSerializer
from auth_app.utils import (
    create_knox_token, build_activation_link, build_deletion_link, build_reset_link, is_valid_email, resolve_knox_token, send_activation_email, send_deletion_email, send_reset_email,
)

User = get_user_model()


class RegistrationView(APIView):
    """Create user (inactive), add Knox token, send activation email."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = RegistrationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        token = create_knox_token(user, hours=24)
        link = build_activation_link(token)
        send_activation_email(user, link)
        data = {"email": user.email, "user_id": user.id,
                "is_active": user.is_active}
        return Response(data, status=status.HTTP_201_CREATED)


class AccountActivationView(APIView):
    """Activate user by body token; delete that Knox token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = AccountActivationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.validated_data["token"]
        obj = resolve_knox_token(token)
        if obj is None:
            return Response({"detail": "Not found."}, status=404)
        user = obj.user
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
        obj.delete()
        data = {"email": user.email, "user_id": user.id,
                "is_active": user.is_active}
        return Response(data, status=200)


class AccountReactivationView(APIView):
    """Send activation email if user exists; always 200 on valid email."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = AccountReactivationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"]
        user = User.objects.filter(email=email).first()
        if user:
            token = create_knox_token(user, hours=24)
            link = build_activation_link(token)
            send_activation_email(user, link)
        return Response({"email": email}, status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    """Check email is valid and not yet registered."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data or {}).get("email", "")
        bad = {"detail": ["Please check your email and try again."]}
        if not email or not is_valid_email(email):
            return Response(bad, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response(bad, status=status.HTTP_400_BAD_REQUEST)
        return Response({"email": email}, status=status.HTTP_200_OK)


class LoginView(APIView):
    """Authenticate by email & password and issue a 12h Knox token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data or {}
        email = data.get("email", "")
        password = data.get("password", "")
        bad = {"detail": ["Please check your login data and try again."]}
        if not email or not password or not is_valid_email(email):
            return Response(bad, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response(bad, status=status.HTTP_400_BAD_REQUEST)
        token = create_knox_token(user, hours=12)
        out = {"email": user.email, "user_id": user.id, "token": token}
        return Response(out, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Delete the current Knox token to log the user out."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token_obj = request.auth
        if hasattr(token_obj, "delete"):
            token_obj.delete()
        msg = {"message": ["Logout successful."]}
        return Response(msg, status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    """Send reset email if user exists; 200 for valid emails, else 400."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data or {}).get("email", "")
        if not email or not is_valid_email(email):
            bad = {"detail": ["Please check your email and try again."]}
            return Response(bad, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first()
        if user:
            token = create_knox_token(user, hours=1)
            link = build_reset_link(token)
            send_reset_email(email, link)
        return Response({"email": email}, status=status.HTTP_200_OK)


class PasswordUpdateView(APIView):
    """Update password for authed user; delete current Knox token."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = PasswordUpdateSerializer(data=request.data)
        if not ser.is_valid():
            bad = {"detail": ["Please check your input and try again."]}
            return Response(bad, status=status.HTTP_400_BAD_REQUEST)
        if request.user.email != ser.validated_data["email"]:
            bad = {"detail": ["Please check your input and try again."]}
            return Response(bad, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        user.set_password(ser.validated_data["password"])
        user.save(update_fields=["password"])
        if hasattr(request.auth, "delete"):
            request.auth.delete()
        out = {"email": user.email, "user_id": user.id}
        return Response(out, status=status.HTTP_200_OK)


class DeregistrationView(APIView):
    """Reauth user, then email 24h deletion link; header Knox auth."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = DeregistrationSerializer(data=request.data)
        if not ser.is_valid():
            bad = {"detail": ["Please check your input and try again."]}
            return Response(bad, status=status.HTTP_400_BAD_REQUEST)

        email = ser.validated_data["email"]
        if email != request.user.email:
            bad = {"detail": ["Please check your input and try again."]}
            return Response(bad, status=status.HTTP_400_BAD_REQUEST)

        authed = authenticate(
            request, email=email, password=ser.validated_data["password"]
        )
        if not authed or authed.pk != request.user.pk:
            bad = {"detail": ["Please check your input and try again."]}
            return Response(bad, status=status.HTTP_400_BAD_REQUEST)

        new_token = create_knox_token(request.user, hours=24)
        link = build_deletion_link(new_token)
        send_deletion_email(request.user, link)
        return Response({"email": email}, status=status.HTTP_200_OK)


class AccountDeletionView(APIView):
    """Delete the authenticated account and current Knox token."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token_obj = request.auth
        user = request.user
        if hasattr(token_obj, "delete"):
            token_obj.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
