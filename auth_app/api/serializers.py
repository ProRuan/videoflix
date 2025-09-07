# Standard libraries

# Third-party suppliers
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from django.utils import timezone

# Local imports
from auth_app.utils import is_strong_password, is_valid_email, send_activation_email, send_password_reset_email, send_account_deletion_email
from token_app.models import Token
from token_app.utils import HEX64_RE, fetch_token, mark_token_used, upsert_token


class RegistrationSerializer(serializers.Serializer):
    """Validate and create a new user; send activation email."""
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    repeated_password = serializers.CharField(write_only=True,
                                              trim_whitespace=False)

    def validate_email(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("Invalid email format.")
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, attrs):
        pwd, rep = attrs.get("password"), attrs.get("repeated_password")
        if not pwd or not rep:
            raise serializers.ValidationError("Missing password fields.")
        if pwd != rep:
            raise serializers.ValidationError("Passwords do not match.")
        if not is_strong_password(pwd):
            raise serializers.ValidationError("Weak password.")
        return attrs

    def create(self, validated_data):
        User = get_user_model()
        email = validated_data["email"]
        user = User.objects.create_user(email=email,
                                        password=validated_data["password"])
        tok = upsert_token(user.id, Token.TYPE_ACTIVATION)
        send_activation_email(email, getattr(
            user, "first_name", ""), tok.value)
        return user


class AccountActivationSerializer(serializers.Serializer):
    """Validate activation token, mark used, return user info."""
    token = serializers.CharField(write_only=True, trim_whitespace=True)

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Missing token.")
        if not HEX64_RE.match(value):
            raise serializers.ValidationError("Invalid token.")
        tok = fetch_token(value)
        if tok is None:
            raise serializers.ValidationError("Token not found.", code="404")
        if tok.type != Token.TYPE_ACTIVATION:
            raise serializers.ValidationError("Invalid token.")
        if tok.used or tok.expired_at <= timezone.now():
            raise serializers.ValidationError("Invalid token.")
        self.context["tok"] = tok
        return value

    def create(self, validated_data):
        tok = self.context["tok"]
        user = tok.user
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
        mark_token_used(tok)
        return user

    def to_representation(self, instance):
        return {"email": instance.email, "user_id": instance.id}


class AccountReactivationSerializer(serializers.Serializer):
    """Create/refresh activation token and send reactivation email."""
    email = serializers.EmailField(write_only=True)

    def validate_email(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("Invalid email.")
        User = get_user_model()
        try:
            self.context["user"] = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.", code="404")
        return value

    def create(self, validated_data):
        user = self.context["user"]
        tok = upsert_token(user.id, Token.TYPE_ACTIVATION)
        send_activation_email(user.email, getattr(user, "first_name", ""),
                              tok.value)
        return user

    def to_representation(self, instance):
        return {"email": instance.email, "user_id": instance.id}


class EmailCheckSerializer(serializers.Serializer):
    """Validate email and check if it exists in the system."""
    email = serializers.EmailField(write_only=True)

    def validate_email(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("Invalid email.")
        return value

    def create(self, validated_data):
        User = get_user_model()
        exists = User.objects.filter(email=validated_data["email"]).exists()
        return {"email": validated_data["email"], "exists": exists}

    def to_representation(self, instance):
        return instance


class LoginSerializer(serializers.Serializer):
    """Authenticate user and return an auth token."""
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email, pwd = attrs.get("email"), attrs.get("password")
        if not email or not is_valid_email(email):
            raise serializers.ValidationError("Invalid email.")
        if not pwd:
            raise serializers.ValidationError("Invalid password.")
        user = authenticate(username=email, password=pwd)
        if not user:
            raise serializers.ValidationError("Invalid password.")
        self.context["user"] = user
        return attrs

    def create(self, validated_data):
        user = self.context["user"]
        tok = upsert_token(user.id, Token.TYPE_AUTH)
        return {"token": tok.value, "email": user.email, "user_id": user.id}

    def to_representation(self, instance):
        return instance


class LogoutSerializer(serializers.Serializer):
    """Mark auth token as used and return user info."""
    token = serializers.CharField(write_only=True, trim_whitespace=True)

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Missing token.")
        if not HEX64_RE.match(value):
            raise serializers.ValidationError("Invalid token.")
        tok = fetch_token(value)
        if tok is None:
            raise serializers.ValidationError("Token not found.", code="404")
        if tok.type != Token.TYPE_AUTH:
            raise serializers.ValidationError("Invalid token.")
        self.context["tok"] = tok
        return value

    def create(self, validated_data):
        tok = self.context["tok"]
        mark_token_used(tok)
        user = tok.user
        return {"email": user.email, "user_id": user.id}

    def to_representation(self, instance):
        return instance


class PasswordResetRequestSerializer(serializers.Serializer):
    """Create/refresh reset token and send reset email."""
    email = serializers.EmailField(write_only=True)

    def validate_email(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("Invalid email.")
        User = get_user_model()
        try:
            self.context["user"] = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.", code="404")
        return value

    def create(self, validated_data):
        user = self.context["user"]
        tok = upsert_token(user.id, Token.TYPE_RESET)
        send_password_reset_email(user.email, getattr(user, "first_name", ""),
                                  tok.value)
        return {"email": user.email}

    def to_representation(self, instance):
        return instance


class PasswordUpdateSerializer(serializers.Serializer):
    """Validate reset token and update password."""
    token = serializers.CharField(write_only=True, trim_whitespace=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    repeated_password = serializers.CharField(write_only=True,
                                              trim_whitespace=False)

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Missing token.")
        if not HEX64_RE.match(value):
            raise serializers.ValidationError("Invalid token.")
        tok = fetch_token(value)
        if tok is None:
            raise serializers.ValidationError("Token not found.", code="404")
        if tok.type != Token.TYPE_RESET or tok.used:
            raise serializers.ValidationError("Invalid token.")
        if tok.expired_at <= timezone.now():
            raise serializers.ValidationError("Invalid token.")
        self.context["tok"] = tok
        return value

    def validate_email(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("Invalid email.")
        tok = self.context.get("tok")
        if tok and tok.user.email != value:
            raise serializers.ValidationError("Invalid email.")
        return value

    def validate(self, attrs):
        p1, p2 = attrs.get("password"), attrs.get("repeated_password")
        if not p1 or not p2:
            raise serializers.ValidationError("Missing password fields.")
        if p1 != p2:
            raise serializers.ValidationError("Passwords do not match.")
        if not is_strong_password(p1):
            raise serializers.ValidationError("Weak password.")
        return attrs

    def create(self, validated_data):
        tok = self.context["tok"]
        user = tok.user
        user.set_password(validated_data["password"])
        user.save(update_fields=["password"])
        mark_token_used(tok)
        return {"email": user.email, "user_id": user.id}

    def to_representation(self, instance):
        return instance


class DeregistrationSerializer(serializers.Serializer):
    """Reauth, create deletion token, send email."""
    token = serializers.CharField(write_only=True, trim_whitespace=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Missing token.")
        if not HEX64_RE.match(value):
            raise serializers.ValidationError("Invalid token.")
        tok = fetch_token(value)
        if tok is None:
            raise serializers.ValidationError("Token not found.", code="404")
        if tok.type != Token.TYPE_AUTH:
            raise serializers.ValidationError("Invalid token.")
        self.context["tok"] = tok
        return value

    def validate_email(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("Invalid email.")
        tok = self.context.get("tok")
        if tok and tok.user.email != value:
            raise serializers.ValidationError("Invalid email.")
        return value

    def validate(self, attrs):
        email, pwd = attrs.get("email"), attrs.get("password")
        if not pwd:
            raise serializers.ValidationError("Invalid password.")
        user = authenticate(username=email, password=pwd)
        if not user:
            raise serializers.ValidationError("Invalid password.")
        self.context["user"] = user
        return attrs

    def create(self, validated_data):
        user = self.context["user"]
        del_tok = upsert_token(user.id, Token.TYPE_DELETION)
        send_account_deletion_email(user.email, getattr(user, "first_name", ""),
                                    del_tok.value)
        return {"email": user.email, "user_id": user.id}

    def to_representation(self, instance):
        return instance

# update template
# ctx = {"user": user, "deletion_link": build_account_deletion_link(token)}


class AccountDeletionSerializer(serializers.Serializer):
    """Validate deletion token and delete the user."""
    token = serializers.CharField(write_only=True, trim_whitespace=True)

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Missing token.")
        if not HEX64_RE.match(value):
            raise serializers.ValidationError("Invalid token.")
        tok = fetch_token(value)
        if tok is None:
            raise serializers.ValidationError("Token not found.", code="404")
        if tok.type != Token.TYPE_DELETION or tok.used:
            raise serializers.ValidationError("Invalid token.")
        if tok.expired_at <= timezone.now():
            raise serializers.ValidationError("Invalid token.")
        self.context["tok"] = tok
        return value

    def create(self, validated_data):
        user = self.context["tok"].user
        uid = user.id
        user.delete()
        return {"deleted_user_id": uid}
