# from django.contrib.auth import authenticate
# from django.contrib.auth.models import User
# from rest_framework import serializers
# from rest_framework.authtoken.models import Token


import re
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Please check your data and try it again.")
        return value

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                'Please check your data and try it again.')
        # Password complexity: min 8 chars, uppercase, lowercase, digit, special
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$'
        if not re.match(pattern, data['password']):
            raise serializers.ValidationError(
                'Please check your data and try it again.')
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user or not user.is_active:
            raise serializers.ValidationError(
                'Please check your data and try it again.')
        return {'user': user}


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Please check your data and try it again.')
        return value


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Check password match
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                'Please check your data and try it again.')
        # Complexity check
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$'
        if not re.match(pattern, data['password']):
            raise serializers.ValidationError(
                'Please check your data and try it again.')
        return data

    def validate_token(self, value):
        try:
            token = User.objects.get(auth_token__key=value).auth_token
        except Exception:
            raise serializers.ValidationError(
                'Please check your data and try it again.')
        return value

    def save(self):
        token_key = self.validated_data['token']
        password = self.validated_data['password']
        token = Token.objects.get(key=token_key)
        user = token.user
        user.set_password(password)
        user.save()
        return token


# class RegistrationSerializer(serializers.ModelSerializer):
#     repeated_password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'repeated_password']
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }

#     def validate_username(self, value):
#         if len(value) < 3:
#             raise serializers.ValidationError(
#                 "Username must be at least 3 characters long.")
#         return value

#     def validate_password(self, value):
#         if len(value) < 8:
#             raise serializers.ValidationError(
#                 "Password must be at least 8 characters long.")
#         if value.isdigit() or value.isalpha():
#             raise serializers.ValidationError(
#                 "Password must contain letters and numbers.")
#         return value

#     def validate(self, data):
#         if data['password'] != data['repeated_password']:
#             raise serializers.ValidationError("Passwords do not match.")
#         return data

#     def create(self, validated_data):
#         validated_data.pop('repeated_password')
#         user = User.objects.create_user(**validated_data)
#         return user


# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = authenticate(
#             username=data['username'], password=data['password'])
#         if not user:
#             raise serializers.ValidationError("Invalid credentials.")
#         data['user'] = user
#         return data


# class ForgotPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         if not User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("Invalid email.")
#         return value


# class ResetPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)
#     repeated_password = serializers.CharField(write_only=True)

#     def validate_password(self, value):
#         if len(value) < 8:
#             raise serializers.ValidationError(
#                 "Password must be at least 8 characters.")
#         if value.isdigit() or value.isalpha():
#             raise serializers.ValidationError(
#                 "Password must contain both letters and numbers.")
#         return value

#     def validate(self, data):
#         if data['password'] != data['repeated_password']:
#             raise serializers.ValidationError("Passwords do not match.")

#         if not User.objects.filter(email=data['email']).exists():
#             raise serializers.ValidationError(
#                 "User with this email does not exist.")

#         return data
