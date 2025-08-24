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
    ForgotPasswordSerializer,
    LoginSerializer,
    RegistrationSerializer,
    ResetPasswordSerializer,
    EmailCheckSerializer,
)
from auth_app.utils import (
    build_auth_response,
    send_confirm_email_email,
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
