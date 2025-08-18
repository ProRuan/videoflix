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
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("token", data)
        self.assertEqual(data["user"], self.user.pk)
        self.assertIn("created_at", data)
        self.assertIn("expired_at", data)

    def test_create_replaces_existing(self):
        # create first
        r1 = self.client.post(
            self.url, {"user": self.user.pk, "type": "activation"}, format="json")
        t1 = r1.json()["token"]
        # create again -> token should change
        r2 = self.client.post(
            self.url, {"user": self.user.pk, "type": "activation"}, format="json")
        t2 = r2.json()["token"]
        self.assertNotEqual(t1, t2)
