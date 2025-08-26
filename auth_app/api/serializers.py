# Third-party suppliers
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token as AuthToken

# Local imports
from auth_app.utils import (
    validate_email_exists,
    validate_email_unique,
    validate_passwords,
    validate_token_key,
)
from token_app.utils import (
    create_token_for_user,
    get_token_and_type_by_value,
    token_expired,
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
        The created user is inactive until account activation.
        """
        return User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )


class AccountActivationSerializer(serializers.Serializer):
    """
    Validates activation token and activates the user on save.

    Validation rules:
      - Token must exist in token_app and be type 'activation' -> otherwise raise
        ValidationError('Token not found.') (view maps this to 404).
      - Token must not be expired or already used -> raise ValidationError('Token expired.') or 'Token already used.'
    save():
      - activates the user
      - marks the activation token as used (instance.used = True)
      - deletes existing DRF auth tokens for that user and returns a fresh auth token instance
    """
    token = serializers.CharField()

    def validate_token(self, value):
        inst, type_str = get_token_and_type_by_value(value)
        if not inst or type_str != "activation":
            raise serializers.ValidationError("Token not found.")
        if token_expired(inst):
            raise serializers.ValidationError("Token expired.")
        if inst.used:
            raise serializers.ValidationError("Token already used.")
        # keep the token instance for save()
        self.instance = inst
        return value

    def save(self):
        token_instance = getattr(self, "instance", None)
        if token_instance is None:
            raise RuntimeError("Called save() without a validated token")

        user = token_instance.user

        # Activate the user
        user.is_active = True
        user.save(update_fields=["is_active"])

        # Consume token: mark used (we keep DB record for audit)
        token_instance.used = True
        token_instance.save(update_fields=["used"])

        # Remove any existing DRF auth tokens for that user and create a fresh one
        AuthToken.objects.filter(user=user).delete()
        new_token = AuthToken.objects.create(user=user)
        return new_token


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


class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        inst = AuthToken.objects.filter(key=value).first()
        if not inst:
            raise serializers.ValidationError("Token not found.")
        self.token_instance = inst
        return value

    def save(self):
        # delete the provided token (logout from that session)
        self.token_instance.delete()
        return None


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Represents a forgot-password serializer.
    Validates presence and format of the email only.
    Existence check is performed in the view to allow returning 404.
    """
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """
    Accepts:
      - token: the reset token provided in the reset link
      - email: the email resolved from token (frontend sends it)
      - password, repeated_password: new password pair

    Validation:
      - email must exist -> raises "User not found." (we map that to 404 in the view)
      - token must exist in token_app and be type 'password_reset' -> raise ValidationError('Token not found or invalid.')
      - token.user.email must match provided email -> ValidationError('Token does not match provided email.')
      - password rules & match -> ValidationError

    save():
      - updates user's password
      - consumes the reset token (marks used)
      - deletes any existing DRF auth Token(s) for the user
      - creates and returns a fresh DRF auth Token instance
    """
    token = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        # Ensure the user exists — we raise an explicit error text that the view will map to 404
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User not found.')
        return value

    def validate(self, data):
        # Validate passwords (strength and match)
        validate_passwords(data['password'], data['repeated_password'])

        # Verify token existence and type
        token_key = data.get('token')
        inst, type_str = get_token_and_type_by_value(token_key)
        if not inst or type_str != "password_reset":
            raise serializers.ValidationError('Token not found or invalid.')

        # Check expiry and used state
        if token_expired(inst):
            raise serializers.ValidationError('Token expired.')
        if inst.used:
            raise serializers.ValidationError('Token already used.')

        # Verify token maps to same user email
        user = inst.user
        if user.email != data.get('email'):
            raise serializers.ValidationError(
                'Token does not match provided email.')

        # Save instance for use in save()
        self.instance = inst
        return data

    def save(self):
        token_instance = getattr(self, "instance", None)
        if token_instance is None:
            raise RuntimeError("Called save() without validated token")

        email = self.validated_data['email']
        password = self.validated_data['password']

        user = User.objects.get(email=email)
        user.set_password(password)
        user.save(update_fields=["password"])

        # Consume token and remove old DRF auth tokens
        token_instance.used = True
        token_instance.save(update_fields=["used"])

        AuthToken.objects.filter(user=user).delete()
        new_token = AuthToken.objects.create(user=user)
        return new_token


class EmailCheckSerializer(serializers.Serializer):
    """
    Represents an email existence check (for registration).
    """
    email = serializers.EmailField()


class DeregistrationSerializer(serializers.Serializer):
    """
    Validates email + password for a deregistration request.
    On save() it creates a single-use account_deletion token and returns the raw token.
    Validation rules:
      - email: must exist -> raise ValidationError('User not found.') (view maps this to 404)
      - password: validated by authenticate(); if invalid -> ValidationError('Invalid credentials.')
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        # Explicit user existence check -> view will map to 404
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User not found.')
        return value

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        # store the user for save()
        self.user = user
        return data

    def save(self):
        # Create deletion token and return raw token string
        token_inst = create_token_for_user(self.user, "deletion")
        raw = token_inst.token
        return {"token": raw, "email": self.user.email, "user_id": self.user.id}


class AccountDeletionSerializer(serializers.Serializer):
    """
    Accepts { token } to perform the actual account deletion (hard-delete).
    Validation rules:
      - token must exist and be of type 'deletion' -> ValidationError('Token not found.')
      - token must not be expired -> ValidationError('Token expired.')
      - token must not be used -> ValidationError('Token already used.')
    save():
      - marks token used (for audit) then deletes the User (hard delete)
      - removes any DRF auth tokens
    """
    token = serializers.CharField()

    def validate_token(self, value):
        inst, type_str = get_token_and_type_by_value(value)
        if not inst or type_str != "deletion":
            raise serializers.ValidationError("Token not found.")
        if token_expired(inst):
            raise serializers.ValidationError("Token expired.")
        if inst.used:
            raise serializers.ValidationError("Token already used.")
        # keep token instance for save()
        self.instance = inst
        return value

    def save(self):
        token_instance = getattr(self, "instance", None)
        if token_instance is None:
            raise RuntimeError("Called save() without a validated token")

        user = token_instance.user

        # Mark token used for audit before deletion
        token_instance.used = True
        token_instance.save(update_fields=["used"])

        # Remove any existing DRF auth tokens for that user
        AuthToken.objects.filter(user=user).delete()

        # Optionally record some audit info here before deletion

        # Finally hard-delete the user (this cascades or runs model delete hooks)
        user.delete()

        # Nothing to return for deletion
        return None


class UserEmailSerializer(serializers.Serializer):
    """
    Accepts { token } and returns { email } on success.

    Validation:
      - token must exist as a DRF AuthToken -> ValidationError('Token not found.')
    save():
      - returns dict {'email': user.email}
    """
    token = serializers.CharField()

    def validate_token(self, value):
        inst = AuthToken.objects.filter(key=value).first()
        if not inst:
            raise serializers.ValidationError("Token not found.")
        # keep the user for save()
        self.user = inst.user
        return value

    def save(self):
        user = getattr(self, "user", None)
        if user is None:
            raise RuntimeError("Called save() without a validated token")
        return {"email": user.email}
