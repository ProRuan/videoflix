from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class TokenCreationSerializer(serializers.Serializer):
    user = serializers.IntegerField()
    type = serializers.ChoiceField(
        choices=["activation", "deletion", "password_reset"])


class TokenCreationResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    type = serializers.CharField()
    user = serializers.IntegerField()
    lifetime = serializers.DurationField()
    created_at = serializers.DateTimeField()
    expired_at = serializers.DateTimeField()


class TokenCheckSerializer(serializers.Serializer):
    token = serializers.CharField()
    used = serializers.BooleanField(required=False)


class TokenCheckResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    type = serializers.CharField()
    user = serializers.IntegerField()
    used = serializers.BooleanField()
