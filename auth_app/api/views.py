from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import ResetPasswordSerializer
from django.contrib.auth.models import User
from .serializers import ForgotPasswordSerializer
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .serializers import ForgotPasswordSerializer, LoginSerializer, RegistrationSerializer, ResetPasswordSerializer

# move to helper file?
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_activation_email(user, activation_link):
    subject = "Activate your Videoflix account"
    from_email = "noreply@videoflix.com"
    to = 'rudolf.sachslehner@gmx.at'
    # to = user.email

    html_content = render_to_string("auth_app/confirm-your-email.html", {
        "user_name": user.first_name or "there",
        "activation_link": activation_link,
        "logo_url": "https://yourdomain.com/static/img/logo.png"  # Or a CDN-hosted logo
    })

    email = EmailMultiAlternatives(subject, "", from_email, [to])
    email.attach_alternative(html_content, "text/html")
    email.send()
    print('sent email successfully')


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            # testing + update urls and values!!
            send_activation_email(user, 'http://localhost:4200/reset-password')

            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 1. Basic approach
# class ForgotPasswordView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = ForgotPasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data['email']
#             # Optionally, trigger sending a reset email here
#             return Response({"email": email}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2.a render_to_string() approach


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            reset_link = 'http://localhost:4200/reset-password'  # Change for production

            html_content = render_to_string(
                "auth_app/reset-your-password.html",
                {"user_name": user.first_name or user.username,
                    "reset_link": reset_link}
            )

            subject = "Reset your Videoflix password"
            from_email = "noreply@videoflix.com"
            to_email = [user.email]

            msg = EmailMultiAlternatives(subject, "", from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return Response({"email": email}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2.b EmailMessage approach
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string

# class ForgotPasswordView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = ForgotPasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data['email']
#             user = User.objects.get(email=email)

#             reset_link = 'http://localhost:4200/reset-password'

#             html_content = render_to_string(
#                 "auth_app/reset-your-password.html",
#                 {"user_name": user.first_name or user.username, "reset_link": reset_link}
#             )

#             subject = "Reset your Videoflix password"
#             from_email = "noreply@videoflix.com"
#             to_email = [user.email]

#             email_message = EmailMessage(subject, html_content, from_email, to_email)
#             email_message.content_subtype = "html"  # Important!
#             email_message.send()

#             return Response({"email": email}, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
