# auth_app/api/serializers.py
# Standard libraries
import re

# Third-party suppliers
from django.contrib.auth import get_user_model
from rest_framework import serializers

# Local imports
from auth_app.utils import (
    validate_email_or_raise,
    validate_email_unique,
    validate_passwords,
)

User = get_user_model()

TOKEN_RE = re.compile(r"^[A-Za-z0-9:_\-]{10,}$")


class RegistrationSerializer(serializers.Serializer):
    """Validate registration data and create a deactivated user."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    repeated_password = serializers.CharField(
        write_only=True, trim_whitespace=False, allow_blank=True
    )

    def validate_email(self, value):
        validate_email_or_raise(value)
        validate_email_unique(value)
        return value

    def validate(self, data):
        validate_passwords(data.get("password"), data.get("repeated_password"))
        return data

    def create(self, validated):
        return User.objects.create_user(
            email=validated["email"],
            password=validated["password"],
            is_active=False,
        )


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
        validate_email_or_raise(value)
        return value


class PasswordUpdateSerializer(serializers.Serializer):
    """Validate email and new password for password update."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    repeated_password = serializers.CharField(
        write_only=True, trim_whitespace=False
    )

    def validate_email(self, value):
        validate_email_or_raise(value)
        return value

    def validate(self, data):
        validate_passwords(data.get("password"), data.get("repeated_password"))
        return data


class DeregistrationSerializer(serializers.Serializer):
    """Validate email and password for deregistration."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value):
        validate_email_or_raise(value)
        return value


class AccountDeletionSerializer(serializers.Serializer):
    """Validate body token for account deletion."""
    token = serializers.CharField()

    def validate_token(self, value):
        if not TOKEN_RE.match(value or ""):
            raise serializers.ValidationError("Invalid token.")
        return value
