# Standard libraries
import logging

# Third-party suppliers
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rq import enqueue
from knox.models import AuthToken

# Local imports
from auth_app.tasks import delete_user_expired_knox_tokens


logger = logging.getLogger(__name__)


@receiver(post_save, sender=AuthToken)
def enqueue_cleanup_on_token_create(sender, instance, created, **kwargs):
    """
    Enqueue background cleanup for the same user's expired Knox tokens
    whenever a new token is created.
    """
    if not created:
        return
    try:
        enqueue(delete_user_expired_knox_tokens, instance.user_id)
    except Exception:
        logger.exception("Failed to enqueue token cleanup task.")
