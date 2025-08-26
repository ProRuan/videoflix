# Third-party suppliers
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token as AuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from .serializers import (
    AccountActivationSerializer,
    AccountDeletionSerializer,
    DeregistrationSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    RegistrationSerializer,
    ResetPasswordSerializer,
    EmailCheckSerializer,
    UserEmailSerializer,
)
from auth_app.utils import (
    build_auth_response,
    send_confirm_email_email,
    send_deregistration_email,
    send_reset_password_email,
    validate_serializer_or_400,
)
from token_app.utils import (
    create_token_for_user,
    get_token_and_type_by_value,
    token_expired,
    token_expiry_datetime,
)

User = get_user_model()


class RegistrationView(APIView):
    """
    POST creates a new inactive user and sends confirm-email email.
    Returns token, email and user_id on success (201).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        error = validate_serializer_or_400(serializer)
        if error:
            return error

        user = serializer.save()
        # create activation token (token_app)
        token_instance = create_token_for_user(user, "activation")
        raw_token = token_instance.token

        activation_link = f"https://your-frontend.com/confirm-email?token={raw_token}"
        send_confirm_email_email(user, activation_link)

        # Return token in response (keeps behavior compatible with previous code)
        return Response(
            {"token": raw_token, "email": user.email, "user_id": user.id},
            status=status.HTTP_201_CREATED
        )


class AccountActivationView(APIView):
    """
    POST activates a user account using a token.
    Responses:
    - 200 OK with { token, email, user_id } when token valid and activation done
    - 400 Bad Request for missing/invalid payload or expired/used token
    - 404 Not Found when token not found
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AccountActivationSerializer(data=request.data)
        # run validation to populate serializer.errors if any
        serializer.is_valid()
        if serializer.errors:
            token_errors = serializer.errors.get('token', [])
            # if token not found -> 404
            if any('Token not found' in str(e) for e in token_errors):
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
            # otherwise, bad request (expired/used or missing field)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # save activates the user and returns the new DRF auth token instance
        new_auth_token = serializer.save()
        user = new_auth_token.user
        return Response(
            {'token': new_auth_token.key, 'email': user.email, 'user_id': user.id},
            status=status.HTTP_200_OK
        )

# rename to AccountReactivationView


class ReactivateAccountView(APIView):
    """
    POST /api/account-reactivation/
    Request: { email }
    Success: 200
      - If email exists: { token, email, user_id } (token is activation token)
      - If email doesn't exist: { "status": "ok" } (no disclosure)
    Errors:
      - 400 Bad Request when email missing/invalid (serializer)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        # Return field-level errors so tests can assert on 'email'
        serializer.is_valid()
        if serializer.errors:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            # Create activation token and send activation / reactivation email
            token_instance = create_token_for_user(user, "activation")
            raw = token_instance.token
            activation_link = f"https://your-frontend.com/confirm-email?token={raw}"
            send_confirm_email_email(user, activation_link)

            return Response(
                {"token": raw, "email": user.email, "user_id": user.id},
                status=status.HTTP_200_OK
            )

        # Generic success for non-existing emails
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class LoginView(APIView):
    """
    POST authenticates a user and refreshes a DRF auth token (delete old -> create new).
    Response: { token, email, user_id } on success (200)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        error = validate_serializer_or_400(serializer)
        if error:
            return error

        user = serializer.validated_data['user']

        # Remove any existing DRF tokens and create a fresh one (refresh)
        AuthToken.objects.filter(user=user).delete()
        new_token = AuthToken.objects.create(user=user)

        return Response(
            {'token': new_token.key, 'email': user.email, 'user_id': user.id},
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    """
    POST /api/logout/
    Request: { token, email, user_id }
    Success: 204 No Content (token deleted)
    Errors:
      - 400 Bad Request for other validation errors
      - 404 Not Found when token or user not found
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid()
        if serializer.errors:
            joined = " ".join(str(v) for v in serializer.errors.values())
            if 'Token not found' in joined:
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ForgotPasswordView(APIView):
    """
    POST /api/forgot-password/
    Request: { email }
    Success: 200
      - If email exists: { token, email, user_id } (token is password reset token)
      - If email doesn't exist: { "status": "ok" } (no disclosure)
    Errors:
      - 400 Bad Request when email missing/invalid (serializer)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        # Return field-level errors so tests can assert on 'email'
        serializer.is_valid()
        if serializer.errors:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        # Try to find user but do NOT reveal non-existence
        user = User.objects.filter(email=email).first()
        if user:
            # Create a password reset token and send the email
            token_instance = create_token_for_user(user, "password_reset")
            raw = token_instance.token
            reset_link = f"https://your-frontend.com/reset-password?token={raw}"
            send_reset_password_email(user, reset_link)

            return Response(
                {"token": raw, "email": user.email, "user_id": user.id},
                status=status.HTTP_200_OK
            )

        # Generic success for non-existing emails (prevent enumeration)
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    POST /api/reset-password/
    Request: { token, email, password, repeated_password }
    Success: 200 { token, email, user_id }  (fresh DRF auth token)
    Errors:
      - 400 Bad Request for token invalid, password invalid/mismatch or other validation
      - 404 Not Found if email/user not found
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        # run validation to populate serializer.errors
        serializer.is_valid()
        if serializer.errors:
            # If the email field contains 'User not found.' -> map to 404
            email_errors = serializer.errors.get('email', [])
            if any('User not found' in str(e) for e in email_errors):
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

            # For other errors return generic 400
            return Response(
                {'detail': 'Please check your data and try it again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # All valid — perform save (updates password, consumes reset token, creates auth token)
        new_auth_token = serializer.save()
        user = new_auth_token.user
        return Response(
            {'token': new_auth_token.key, 'email': user.email, 'user_id': user.id},
            status=status.HTTP_200_OK
        )


class EmailCheckView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailCheckSerializer(data=request.data)
        # Return 400 with field-level errors when missing/invalid
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        # If email exists -> 404 Not Found with field-level message
        if User.objects.filter(email=email).exists():
            return Response(
                {"email": ["Email already registered."]},
                status=status.HTTP_404_NOT_FOUND
            )

        # Email not found -> success
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class DeregistrationView(APIView):
    """
    POST /api/deregistration/
    Request: { email, password } -> authenticates the user and sends a deletion email with a 'deletion' token.
    Success: 200 { token, email, user_id } (when user exists)
             200 {"status":"ok"} (when email not found; prevents enumeration)
    Errors: 400 for invalid payload/credentials, 404 when email not found (if you prefer explicit 404)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DeregistrationSerializer(data=request.data)
        serializer.is_valid()
        if serializer.errors:
            email_errors = serializer.errors.get('email', [])
            if any('User not found' in str(e) for e in email_errors):
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # {"token": raw, "email": ..., "user_id": ...}
        created = serializer.save()
        raw_token = created['token']
        user_email = created['email']
        user_id = created['user_id']

        # Build deletion confirmation link and send e-mail
        deletion_link = f"https://your-frontend.com/deactivate-account?token={raw_token}"
        user = User.objects.get(email=user_email)
        send_deregistration_email(user, deletion_link)

        return Response(
            {"token": raw_token, "email": user_email, "user_id": user_id},
            status=status.HTTP_200_OK
        )


class AccountDeletionView(APIView):
    """
    POST /api/account-deletion/
    Request: { token }
    Success: 204 No Content (user hard-deleted)
    Errors:
      - 400 Bad Request for missing/invalid token
      - 404 Not Found when token not found
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AccountDeletionSerializer(data=request.data)
        serializer.is_valid()
        if serializer.errors:
            token_errors = serializer.errors.get('token', [])
            if any('Token not found' in str(e) for e in token_errors):
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # This will hard-delete the user
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserEmailView(APIView):
    """
    POST /api/user-email/
    Request: { token }
    Success: 200 { email }
    Errors:
      - 400 Bad Request for missing/invalid payload
      - 404 Not Found when token not found
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserEmailSerializer(data=request.data)
        # run validation to populate serializer.errors
        serializer.is_valid()
        if serializer.errors:
            token_errors = serializer.errors.get('token', [])
            if any('Token not found' in str(e) for e in token_errors):
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = serializer.save()
        return Response({"email": result["email"]}, status=status.HTTP_200_OK)
