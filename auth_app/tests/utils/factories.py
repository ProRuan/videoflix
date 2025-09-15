# Third-party suppliers
from django.contrib.auth import get_user_model

User = get_user_model()


def make_user(email="john.doe@mail.com", **kwargs):
    """Create and return a user."""
    pw = kwargs.pop("password", "Test123!")
    return User.objects.create_user(email=email, password=pw, **kwargs)
