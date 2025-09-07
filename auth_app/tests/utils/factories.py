# Standard libraries

# Third-party suppliers
from django.contrib.auth import get_user_model

# Local imports


def make_user(email: str):
    """Create a user with a safe default password."""
    User = get_user_model()
    return User.objects.create_user(email=email, password="Test123!")
