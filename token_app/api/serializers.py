# token_app/api/serializers.py
# Standard libraries
import re

# Third-party suppliers
from rest_framework import serializers

# Local imports


TOKEN_RE = re.compile(r"^[A-Za-z0-9:_\-]{10,}$")


class ActivationTokenCheckSerializer(serializers.Serializer):
    """Validate activation token format."""
    token = serializers.CharField()

    def validate_token(self, value):
        if not TOKEN_RE.match(value or ""):
            raise serializers.ValidationError("Invalid token.")
        return value
