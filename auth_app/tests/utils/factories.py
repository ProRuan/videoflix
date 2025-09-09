# Standard libraries

# Third-party suppliers
from django.contrib.auth import get_user_model

# Local imports

User = get_user_model()


def make_user(email="john.doe@mail.com", **kwargs):
    """Create and return a user."""
    pw = kwargs.pop("password", "Test123!")
    return User.objects.create_user(email=email, password=pw, **kwargs)
