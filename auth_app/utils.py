# Third-party suppliers
import re
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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


def send_templated_email(
    subject: str, template_name: str, context: dict,
    to_email: str, from_email: str = 'info@Videoflix.com'
) -> None:
    """
    Renders the given template with context and sends it as an HTML email.
    """
    html_body = render_to_string(template_name, context)
    msg = EmailMultiAlternatives(subject, "", from_email, [to_email])
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=True)


def send_confirm_email_email(user, activation_link):
    """
    Renders the confirm-email template and sends it as an HTML email.
    """
    send_templated_email(
        subject="Confirm your email",
        template_name="auth_app/confirm-email.html",
        context={
            "email": user.email,
            "activation_link": activation_link,
        },
        to_email=user.email,
    )


def send_reset_password_email(user, reset_link):
    """
    Renders the reset-password template and sends it as an HTML email.
    """
    send_templated_email(
        subject="Reset your password",
        template_name="auth_app/reset-password.html",
        context={
                "reset_link": reset_link,
        },
        to_email=user.email,
    )


# update data!!!
def send_deregistration_email(user, deletion_link):
    """
    Renders the confirm-email template and sends it as an HTML email.
    """
    send_templated_email(
        subject="Confirm account deletion",
        template_name="auth_app/confirm-account-deletion.html",
        context={
            "user": user,
            "email": user.email,
            "deletion_link": deletion_link,
        },
        to_email=user.email,
    )

# def send_deregistration_email(user, deletion_link):
#     context = {
#         "user": user,
#         "email": user.email,
#         "deletion_link": deletion_link,
#     }
#     subject = "Confirm account deletion"
#     html_body = render_to_string("auth_app/confirm-deregistration.html", context)
#     msg = EmailMessage(subject=subject, body=html_body, to=[user.email])
#     msg.content_subtype = "html"
#     msg.send()
