from .serializers import LoginSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer

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
