# Standard libraries
import re

# Third-party suppliers
from rest_framework import serializers


TOKEN_RE = re.compile(r"^[A-Za-z0-9:_\-]{10,}$")


class ActivationTokenCheckSerializer(serializers.Serializer):
    """
    Class representing an activation token check serializer.

    Validates an account activation token.
    """
    token = serializers.CharField()

    def validate_token(self, value):
        """Validate account activation token."""
        if not TOKEN_RE.match(value or ""):
            raise serializers.ValidationError("Invalid token.")
        return value
