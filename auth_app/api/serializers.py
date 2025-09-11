# Standard libraries
import re

# Third-party suppliers
from django.contrib.auth import get_user_model
from rest_framework import serializers

# Local imports
from auth_app.utils import is_valid_email, is_strong_password

User = get_user_model()


TOKEN_RE = re.compile(r"^[A-Za-z0-9:_\-]{10,}$")


class RegistrationSerializer(serializers.Serializer):
    """Validate registration payload and create a deactivated user."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    repeated_password = serializers.CharField(
        write_only=True, trim_whitespace=False, allow_blank=True
    )

    def validate_email(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("Enter a valid email address.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_password(self, value):
        ok, msg = is_strong_password(value)
        if not ok:
            raise serializers.ValidationError(msg)
        return value

    def validate(self, data):
        p1 = data.get("password") or ""
        p2 = data.get("repeated_password") or ""
        if not p1:
            return data
        if p1 != p2:
            raise serializers.ValidationError(
                {"password": ["Passwords must match."]}
            )
        return data

    def create(self, validated):
        user = User.objects.create_user(
            email=validated["email"],
            password=validated["password"],
            is_active=False,
        )
        return user


class ActivationTokenCheckSerializer(serializers.Serializer):
    """Validate activation token format."""
    token = serializers.CharField()

    def validate_token(self, value):
        if not TOKEN_RE.match(value or ""):
            raise serializers.ValidationError("Invalid token.")
        return value


class AccountActivationSerializer(serializers.Serializer):
    """Validate body token for account activation."""
    token = serializers.CharField()

    def validate_token(self, value):
        if not TOKEN_RE.match(value or ""):
            raise serializers.ValidationError("Invalid token.")
        return value


class AccountReactivationSerializer(serializers.Serializer):
    """Validate email input for account reactivation."""
    email = serializers.EmailField()

    def validate_email(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value


class PasswordUpdateSerializer(serializers.Serializer):
    """Validate email and new password for password update."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    repeated_password = serializers.CharField(
        write_only=True, trim_whitespace=False
    )

    def validate_email(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate_password(self, value):
        ok, msg = is_strong_password(value)
        if not ok:
            raise serializers.ValidationError(msg)
        return value

    def validate(self, data):
        if data.get("password") != data.get("repeated_password"):
            raise serializers.ValidationError(
                {"password": ["Passwords must match."]}
            )
        return data


class DeregistrationSerializer(serializers.Serializer):
    """Validate email and password for deregistration."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value


class AccountDeletionSerializer(serializers.Serializer):
    """Validate body token for account deletion."""
    token = serializers.CharField()

    def validate_token(self, value):
        if not TOKEN_RE.match(value or ""):
            raise serializers.ValidationError("Invalid token.")
        return value
