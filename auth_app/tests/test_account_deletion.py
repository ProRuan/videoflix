# auth_app/tests/test_account_deletion.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from token_app.utils import create_token_for_user

User = get_user_model()


@pytest.mark.django_db
class TestAccountDeletionEndpoint:
    endpoint = reverse('account-deletion')

    def setup_method(self):
        self.user = User.objects.create_user(
            email='delete@example.com',
            password='StrongP@ss1'
        )

    def test_account_deletion_success(self):
        token_inst = create_token_for_user(self.user, "deletion")
        raw = token_inst.token

        client = APIClient()
        response = client.post(self.endpoint, {'token': raw}, format='json')

        assert response.status_code == 204

        # user should be removed from DB
        assert not User.objects.filter(id=self.user.id).exists()

        # token object may be cascade-deleted with user; don't assume it exists

    def test_account_deletion_token_not_found(self):
        client = APIClient()
        response = client.post(self.endpoint, {'token': 'nope'}, format='json')
        assert response.status_code == 404

    @pytest.mark.parametrize("payload, expected_field", [
        ({}, 'token'),
        ({'token': ''}, 'token'),
    ])
    def test_account_deletion_invalid_request(self, payload, expected_field):
        client = APIClient()
        response = client.post(self.endpoint, payload, format='json')
        assert response.status_code == 400
        body = response.json()
        assert expected_field in body
