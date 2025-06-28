# Third-party suppliers
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

# Local imports
from auth_app.utils import (
    validate_email_exists,
    validate_email_unique,
    validate_passwords,
    validate_token_key,
)

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    """
    Represents a registration serializer.
    Provides methods to validate email and passwords.
    Creates a user based on valid email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """
        Validate an email for uniqueness.
        """
        validate_email_unique(value)
        return value

    def validate(self, data):
        """
        Validate passwords for validity and match.
        """
        validate_passwords(data['password'], data['repeated_password'])
        return data

    def create(self, validated_data):
        """
        Create a user by validated email and password.
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
        Validate an email for existence.
        """
        validate_email_exists(value)
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """
    Represents a reset-password serializer.
    Provides methods to validate token and passwords.
    Updates a user password by validated data.
    """
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate passwords for validity and match.
        """
        validate_passwords(data['password'], data['repeated_password'])
        return data

    def validate_token(self, value):
        """
        Validate a token for existence.
        """
        validate_token_key(value)
        return value

    def save(self):
        """
        Update a user password.
        """
        token_key = self.validated_data['token']
        password = self.validated_data['password']
        token = Token.objects.get(key=token_key)
        user = token.user
        user.set_password(password)
        user.save()
        return token
