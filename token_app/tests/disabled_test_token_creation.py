from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()


class TokenCreationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="bob", email="bob@example.com", password="pass"
        )
        self.url = reverse("token-creation")

    def test_create_activation_token(self):
        resp = self.client.post(
            self.url, {"user": self.user.pk, "type": "activation"}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("token", data)
        self.assertEqual(data["user"], self.user.pk)
        self.assertEqual(data["type"], "activation")
        self.assertIn("created_at", data)
        self.assertIn("expired_at", data)
        self.assertIn("lifetime", data)

    def test_create_replaces_existing(self):
        r1 = self.client.post(
            self.url, {"user": self.user.pk, "type": "activation"}, format="json")
        t1 = r1.json()["token"]
        r2 = self.client.post(
            self.url, {"user": self.user.pk, "type": "activation"}, format="json")
        t2 = r2.json()["token"]
        self.assertNotEqual(t1, t2)

    def test_missing_fields_returns_400(self):
        r = self.client.post(self.url, {}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_invalid_type_returns_400(self):
        r = self.client.post(
            self.url, {"user": self.user.pk, "type": "nope"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_user_not_found_returns_404(self):
        r = self.client.post(
            self.url, {"user": 99999, "type": "activation"}, format="json")
        self.assertEqual(r.status_code, 404)
