# Third-party suppliers
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

# Local imports
from auth_app.utils import (
    validate_email_exists,
    validate_email_unique,
    validate_passwords,
    validate_token_key,
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
    - token: required
    - validate_token raises serializers.ValidationError('Token not found.') -> view maps to 404
    - save() activates the user, deletes any existing tokens for that user (consumes
      the activation token) and creates & returns a fresh auth token instance.
    """
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            Token.objects.get(key=value)
        except Token.DoesNotExist:
            raise serializers.ValidationError('Token not found.')
        return value

    def save(self):
        token_key = self.validated_data['token']
        # Get the token and the associated user
        token_obj = Token.objects.get(key=token_key)
        user = token_obj.user

        # Activate the user
        user.is_active = True
        user.save()

        # Delete any existing tokens for that user (consume activation/reset tokens)
        Token.objects.filter(user=user).delete()

        # Create a fresh auth token and return it for immediate use
        new_token = Token.objects.create(user=user)
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


# class ForgotPasswordSerializer(serializers.Serializer):
#     """
#     Represents a forgot-password serializer.
#     Provides methods to validate an email.
#     """
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         """
#         Validate an email for existence.
#         """
#         validate_email_exists(value)
#         return value

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Represents a forgot-password serializer.
    Validates presence and format of the email only.
    Existence check is performed in the view to allow returning 404.
    """
    email = serializers.EmailField()


# class ResetPasswordSerializer(serializers.Serializer):
#     """
#     Represents a reset-password serializer.
#     Provides methods to validate token and passwords.
#     Updates a user password by validated data.
#     """
#     token = serializers.CharField()
#     password = serializers.CharField(write_only=True)
#     repeated_password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         """
#         Validate passwords for validity and match.
#         """
#         validate_passwords(data['password'], data['repeated_password'])
#         return data

#     def validate_token(self, value):
#         """
#         Validate a token for existence.
#         """
#         validate_token_key(value)
#         return value

#     def save(self):
#         """
#         Update a user password.
#         """
#         token_key = self.validated_data['token']
#         password = self.validated_data['password']
#         token = Token.objects.get(key=token_key)
#         user = token.user
#         user.set_password(password)
#         user.save()
#         return token


class ResetPasswordSerializer(serializers.Serializer):
    """
    Accepts:
      - token: the reset token provided in the reset link
      - email: the email resolved from token (frontend sends it)
      - password, repeated_password: new password pair
    Validation:
      - email must exist -> raises "User not found." (we map that to 404 in the view)
      - token must exist and match the email -> serializer raises ValidationError (mapped to 400)
      - password rules & match -> ValidationError (mapped to 400)
    save():
      - updates user's password
      - deletes any existing Token(s) for the user (consumes reset token)
      - creates and returns a fresh auth Token instance
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

        # Verify token existence
        token_key = data.get('token')
        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            raise serializers.ValidationError('Token not found or invalid.')

        # Verify token maps to same user email
        user = token.user
        if user.email != data.get('email'):
            # Token does not belong to the provided email
            raise serializers.ValidationError(
                'Token does not match provided email.')

        # Everything OK
        return data

    def save(self):
        email = self.validated_data['email']
        password = self.validated_data['password']

        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        # Remove any existing tokens for user (consume/reset the reset token)
        Token.objects.filter(user=user).delete()

        # Create a fresh auth token for immediate use and return it
        new_token = Token.objects.create(user=user)
        return new_token


class EmailCheckSerializer(serializers.Serializer):
    """
    Represents a forgot-password serializer.
    Provides methods to validate an email.
    """
    email = serializers.EmailField()

    # def validate_email(self, value):
    #     """
    #     Validate an email for existence.
    #     """
    #     validate_email_exists(value)
    #     return value
