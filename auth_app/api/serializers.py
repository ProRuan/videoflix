# Third-party suppliers
import re
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    """
    Represents a registration serializer.
    Provides methods to validate email and passwords.
    Creates user based on valid email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """
        Validate email for uniqueness.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Please check your data and try it again."
            )
        return value

    def validate(self, data):
        """
        Validate passwords for validity and match.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                'Please check your data and try it again.'
            )
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$'
        if not re.match(pattern, data['password']):
            raise serializers.ValidationError(
                'Please check your data and try it again.'
            )
        return data

    def create(self, validated_data):
        """
        Create user by validated email and password.
        """
        return User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )


class LoginSerializer(serializers.Serializer):
    """
    Represents a login serializer.
    Provides methods to authenticate a user.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate user data and user account.
        """
        user = authenticate(
            email=data['email'], password=data['password']
        )
        if not user or not user.is_active:
            raise serializers.ValidationError(
                'Please check your data and try it again.'
            )
        return {'user': user}


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Represents a forgot-password serializer.
    Provides methods to validate an email.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Validate email for existence.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Please check your data and try it again.'
            )
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """
    Represents a reset-password serializer.
    Provides methods to validate token and passwords.
    Updates user password by validated data.
    """
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate passwords for validity and match.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                'Please check your data and try it again.'
            )
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$'
        if not re.match(pattern, data['password']):
            raise serializers.ValidationError(
                'Please check your data and try it again.'
            )
        return data

    def validate_token(self, value):
        """
        Validate token for existence.
        """
        try:
            Token.objects.get(key=value)
        except Token.DoesNotExist:
            raise serializers.ValidationError(
                'Please check your data and try it again.'
            )
        return value

    def save(self):
        """
        Update user password.
        """
        token_key = self.validated_data['token']
        password = self.validated_data['password']
        token = Token.objects.get(key=token_key)
        user = token.user
        user.set_password(password)
        user.save()
        return token
