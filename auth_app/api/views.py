# Third-party suppliers
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
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

User = get_user_model()


# class RegistrationView(APIView):
#     """
#     Represents a registration view.
#         - POST creates a new user and triggers a confirm-email email.
#     """
#     permission_classes = [AllowAny]

#     def post(self, request):
#         """
#         Post user registration data.
#         Triggers a confirm-email email.
#         Returns token, email and user_id.
#         """
#         serializer = RegistrationSerializer(data=request.data)
#         error = validate_serializer_or_400(serializer)
#         if error:
#             return error
#         user = serializer.save()
#         view_payload, view_status = build_auth_response(
#             user, status.HTTP_201_CREATED)
#         activation_link = f"https://your-frontend.com/activate?token={view_payload['token']}"
#         send_confirm_email_email(user, activation_link)
#         return Response(view_payload, status=view_status)


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
        # create activation token (returned in response)
        token, _ = Token.objects.get_or_create(user=user)
        activation_link = f"https://your-frontend.com/confirm-email?token={token.key}"
        send_confirm_email_email(user, activation_link)

        return Response(
            {"token": token.key, "email": user.email, "user_id": user.id},
            status=status.HTTP_201_CREATED
        )


class AccountActivationView(APIView):
    """
    POST activates a user account using a token.
    Responses:
    - 200 OK with {email, user_id} when token valid and activation done
    - 400 Bad Request for missing/invalid payload
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
            # otherwise, bad request (e.g. missing field, invalid format)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # save activates the user and deletes the token
        user = serializer.save()
        return Response(
            {'email': user.email, 'user_id': user.id},
            status=status.HTTP_200_OK
        )


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


# class ForgotPasswordView(APIView):
#     """
#     Represents a forgot-password view.
#         - POST triggers a reset-password email.
#     """
#     permission_classes = [AllowAny]

#     def post(self, request):
#         """
#         Post user email.
#         Triggers a reset-password email.
#         Returns token, email and user_id.
#         """
#         serializer = ForgotPasswordSerializer(data=request.data)
#         error = validate_serializer_or_400(serializer)
#         if error:
#             return error
#         user = User.objects.get(email=serializer.validated_data['email'])
#         view_payload, view_status = build_auth_response(
#             user, status.HTTP_200_OK)
#         reset_link = f"https://your-frontend.com/reset-password?token={view_payload['token']}"
#         send_reset_password_email(user, reset_link)
#         return Response(view_payload, status=view_status)


class ForgotPasswordView(APIView):
    """
    Represents a forgot-password view.
        - POST triggers a reset-password email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Post user email.
        Returns 200 with {email, user_id} when email exists,
        404 if email not found, 400 for serializer errors.
        """
        serializer = ForgotPasswordSerializer(data=request.data)
        error = validate_serializer_or_400(serializer)
        if error:
            return error

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"email": ["Email not found."]},
                status=status.HTTP_404_NOT_FOUND
            )

        # Ensure a token exists for the reset link, but don't return it in the API response
        token, _ = Token.objects.get_or_create(user=user)
        reset_link = f"https://your-frontend.com/reset-password?token={token.key}"
        send_reset_password_email(user, reset_link)

        return Response(
            {"email": user.email, "user_id": user.id},
            status=status.HTTP_200_OK
        )


# # update test due to permission change
# class ResetPasswordView(APIView):
#     """
#     Represents a reset-password view.
#         - POST updates a user´s password.
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         """
#         Post new passwords.
#         Returns token, email and user_id.
#         """
#         serializer = ResetPasswordSerializer(data=request.data)
#         error = validate_serializer_or_400(serializer)
#         if error:
#             return error
#         token = serializer.save()
#         user = token.user
#         return Response(
#             {'token': token.key, 'email': user.email, 'user_id': user.id},
#             status=status.HTTP_200_OK
#         )

#  the user must be authenticated?!
class ResetPasswordView(APIView):
    """
    Accepts: { email, password, repeated_password }
    - 400 Bad Request when serializer invalid (missing/invalid passwords => generic message)
    - 200 OK on success with { email, user_id }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        error = validate_serializer_or_400(serializer)
        if error:
            return error

        user = serializer.save()
        return Response(
            {'email': user.email, 'user_id': user.id},
            status=status.HTTP_200_OK
        )


# class EmailCheckView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = EmailCheckSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         email = serializer.validated_data['email']
#         if User.objects.filter(email=email).exists():
#             return Response({"email": ["Email already registered."]}, status=status.HTTP_400_BAD_REQUEST)

#         return Response({"status": "ok"}, status=status.HTTP_200_OK)

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
