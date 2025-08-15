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
    - validate_token raises serializers.ValidationError('Token not found.') -> view will map to 404
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
        token = Token.objects.get(key=token_key)
        user = token.user
        user.is_active = True
        user.save()
        # remove token to prevent reuse
        token.delete()
        return user


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
    Reset-password serializer:
      - email: user's email (populated by frontend via email-check + token in URL)
      - password, repeated_password: new password pair
    On save() it sets the user's password and deletes any Token(s) for that user
    so the token used for reset is not kept.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """
        Ensure email exists (so we can set the password for a real account).
        Uses the same generic ValidationError message as other validators.
        """
        validate_email_exists(value)
        return value

    def validate(self, data):
        """
        Validate password rules and that both passwords match.
        """
        validate_passwords(data['password'], data['repeated_password'])
        return data

    def save(self):
        """
        Update the user's password and remove any tokens for that user
        (we do not keep the token after the reset).
        Returns the user instance.
        """
        email = self.validated_data['email']
        password = self.validated_data['password']
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        # remove any existing tokens (activation/reset/auth tokens reused previously)
        Token.objects.filter(user=user).delete()
        return user


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
