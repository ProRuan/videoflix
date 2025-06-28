# Third-party suppliers
import re
from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

User = get_user_model()

PASSWORD_PATTERN = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$'
)


def validate_passwords(password: str, repeated_password: str) -> None:
    """
    Validate passwords for validity and match.
    A password has at least
        - 8 chars
        - 1 uppercase,
        - 1 lowercase,
        - 1 digit,
        - 1 special char.
    """
    from rest_framework import serializers

    if password != repeated_password:
        raise serializers.ValidationError(
            'Please check your data and try it again.'
        )
    if not PASSWORD_PATTERN.match(password):
        raise serializers.ValidationError(
            'Please check your data and try it again.'
        )


def validate_email_unique(value: str) -> None:
    """
    Validate an email for uniqueness.
    That means no existing user has this email.
    """
    if User.objects.filter(email=value).exists():
        raise serializers.ValidationError(
            'Please check your data and try it again.'
        )


def validate_email_exists(value: str) -> None:
    """
    Validate an email for existence.
    """
    if not User.objects.filter(email=value).exists():
        raise serializers.ValidationError(
            'Please check your data and try it again.'
        )


def validate_token_key(token_key: str) -> None:
    """
    Validate a provided auth token for existence.
    """
    from rest_framework.authtoken.models import Token as _T
    if not Token.objects.filter(key=token_key).exists():
        raise serializers.ValidationError(
            'Please check your data and try it again.'
        )


def validate_serializer_or_400(serializer):
    """
    Validate a serializer.
    Returns status code 400 on failure, otherwise none.
    """
    if not serializer.is_valid():
        return Response(
            {'detail': 'Please check your data and try it again.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return None


def build_auth_response(user, status_code):
    """
    Returns (payload, status_code) for a user’s auth token.
    """
    token, provided = Token.objects.get_or_create(user=user)
    return (
        {'token': token.key, 'email': user.email, 'user_id': user.id},
        status_code
    )
