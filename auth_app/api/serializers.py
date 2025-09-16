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

TOKEN_RE = re.compile(r"^[A-Za-z0-9:_\-]{64,}$")


class RegistrationSerializer(serializers.Serializer):
    """
    Class representing a registration serializer.

    Validates registration data and creates a deactivated user.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    repeated_password = serializers.CharField(
        write_only=True, trim_whitespace=False, allow_blank=True
    )

    def validate_email(self, value):
        """Validate registration email."""
        validate_email_or_raise(value)
        validate_email_unique(value)
        return value

    def validate(self, data):
        """Validate registration passwords."""
        validate_passwords(data.get("password"), data.get("repeated_password"))
        return data

    def create(self, validated):
        """Create deactivated user."""
        return User.objects.create_user(
            email=validated["email"],
            password=validated["password"],
            is_active=False,
        )


class AccountActivationSerializer(serializers.Serializer):
    """
    Class representing an account activation serializer.

    Validates token for account activation.
    """
    token = serializers.CharField()

    def validate_token(self, value):
        """Validate account activation token."""
        if not TOKEN_RE.match(value or ""):
            raise serializers.ValidationError("Invalid token.")
        return value


class AccountReactivationSerializer(serializers.Serializer):
    """
    Class representing an account reactivation serializer.

    Validates email for account reactivation.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """Validate email."""
        validate_email_or_raise(value)
        return value


class PasswordUpdateSerializer(serializers.Serializer):
    """
    Class representing a password update serializer.

    Validate email and new password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    repeated_password = serializers.CharField(
        write_only=True, trim_whitespace=False
    )

    def validate_email(self, value):
        """Validate email."""
        validate_email_or_raise(value)
        return value

    def validate(self, data):
        """Validate passwords."""
        validate_passwords(data.get("password"), data.get("repeated_password"))
        return data


class DeregistrationSerializer(serializers.Serializer):
    """
    Class representing a deregistration serializer.

    Validates email and password for deregistration.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value):
        """Validate email."""
        validate_email_or_raise(value)
        return value
