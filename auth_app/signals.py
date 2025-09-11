# Third-party suppliers
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rq import enqueue
from knox.models import AuthToken

# Local imports
from auth_app.tasks import delete_expired_knox_tokens


@receiver(post_save, sender=AuthToken)
def enqueue_cleanup_on_token_create(sender, instance, created, **kwargs):
    """Enqueue background cleanup when a Knox token is created."""
    if created:
        try:
            enqueue(delete_expired_knox_tokens)
        except Exception:
            pass
