# Third-party suppliers
from django.contrib.auth import get_user_model
from rest_framework import serializers

# Local imports
from token_app.utils import HEX64_RE, fetch_token


class TokenCheckSerializer(serializers.Serializer):
    """Validate token and return user info if valid."""
    token = serializers.CharField(write_only=True, trim_whitespace=True)

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Missing token.")
        if not HEX64_RE.match(value):
            raise serializers.ValidationError("Invalid token pattern.")
        tok = fetch_token(value)
        if tok is None:
            raise serializers.ValidationError("Token not found.", code="404")
        User = get_user_model()
        if not User.objects.filter(pk=tok.user_id).exists():
            raise serializers.ValidationError("Token not found.", code="404")
        if tok.used:
            raise serializers.ValidationError("Token already used.")
        from django.utils import timezone
        if tok.expired_at <= timezone.now():
            raise serializers.ValidationError("Token expired.")
        self.context["token_obj"] = tok
        return value

    def to_representation(self, instance):
        tok = self.context["token_obj"]
        return {"token": tok.value, "email": tok.user.email,
                "user_id": tok.user.id}
