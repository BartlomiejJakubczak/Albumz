import pytest
from django.contrib.auth import get_user_model
from random import randint
from .utils import random_user_rating, random_string

from ..domain.models import Album


User = get_user_model()
user_password = "testpass"
username = "testuser"


@pytest.fixture
def user_factory(db):
    def create_user(username=username, password=user_password, **extra_fields):
        user = User.objects.create_user(username=username, password=password, **extra_fields)
        return user
    return create_user


@pytest.fixture
def auth_user(user_factory):
    return user_factory()


@pytest.fixture
def domain_user(auth_user):
    return auth_user.albumz_user


@pytest.fixture
def authenticated_client(client, auth_user):
    client.login(username=auth_user.username, password=user_password)
    return client


@pytest.fixture
def albums_factory(db, domain_user):
    def create_albums(owned, count=randint(2, 10), user=None):
        albums_in_collection = []
        if user is None:
            user = domain_user
        for _ in range(count):
            albums_in_collection.append(
                Album.objects.create(
                    title=random_string(),
                    artist=random_string(),
                    user=user,
                    owned=owned,
                    user_rating = random_user_rating(),
                )
            )
        return albums_in_collection
    return create_albums
