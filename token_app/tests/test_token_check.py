from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from token_app.utils import create_token_for_user

User = get_user_model()


class TokenCheckTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="sue", email="sue@example.com", password="pw"
        )
        self.create_url = reverse("token-creation")
        self.check_url = reverse("token-check")

    def test_check_token_success(self):
        inst = create_token_for_user(self.user, "password_reset")
        resp = self.client.post(
            self.check_url, {"token": inst.token}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["token"], inst.token)
        self.assertEqual(data["user"], self.user.pk)
        self.assertFalse(data["used"])
        self.assertEqual(data["type"], "password_reset")

    def test_set_used_true(self):
        inst = create_token_for_user(self.user, "password_reset")
        resp = self.client.post(
            self.check_url, {"token": inst.token, "used": True}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["used"])
        # confirm DB updated
        inst.refresh_from_db()
        self.assertTrue(inst.used)

    def test_check_token_not_found(self):
        resp = self.client.post(
            self.check_url, {"token": "nonexistent"}, format="json")
        self.assertEqual(resp.status_code, 404)

    def test_check_token_expired_returns_400(self):
        inst = create_token_for_user(self.user, "password_reset")
        # force created_at far in the past
        inst.created_at = timezone.now() - (inst.lifetime + timedelta(seconds=10))
        inst.save(update_fields=["created_at"])
        resp = self.client.post(
            self.check_url, {"token": inst.token}, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_check_already_used_returns_400(self):
        inst = create_token_for_user(self.user, "password_reset")
        inst.used = True
        inst.save(update_fields=["used"])
        resp = self.client.post(
            self.check_url, {"token": inst.token}, format="json")
        self.assertEqual(resp.status_code, 400)
