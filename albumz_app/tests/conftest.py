import pytest


@pytest.fixture
def auth_client(client, auth_user, test_password):
    client.login(username=auth_user.username, password=test_password)
    return client
