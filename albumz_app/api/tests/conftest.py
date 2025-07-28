import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_api_client(api_client, auth_user, test_password):
    api_client.login(username=auth_user.username, password=test_password)
    return api_client
