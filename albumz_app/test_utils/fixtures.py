from random import randint

import pytest
from django.contrib.auth import get_user_model

from ..constants import TEST_PASSWORD
from ..test_utils.utils import (
    present_date,
    random_string,
    random_user_genre,
    random_user_rating,
)

User = get_user_model()
user_password = TEST_PASSWORD
username = "testuser"


@pytest.fixture
def test_password():
    return user_password


@pytest.fixture
def user_factory(db):
    def create_user(username=username, password=user_password, **extra_fields):
        user = User.objects.create_user(
            username=username, password=password, **extra_fields
        )
        return user

    return create_user


@pytest.fixture
def auth_user(user_factory):
    return user_factory()


@pytest.fixture
def domain_user(auth_user):
    return auth_user.albumz_user


@pytest.fixture
def albums_factory(db, domain_user):
    def create_albums(owned=None, count=randint(2, 10), user=None, mix=False):
        if user is None:
            user = domain_user
        if mix and owned is not None:
            raise AttributeError("'owned' and 'mix' cannot be set simultaneously.")
        if not mix and owned is None:
            raise AttributeError("Either 'owned' or 'mix' parameter has to be set.")

        def create_album(owned):
            return user.albums.create(
                title=random_string(),
                artist=random_string(),
                genre=random_user_genre(),
                pub_date=present_date(),
                user_rating=random_user_rating(),
                owned=owned,
            )

        albums = []
        if mix:
            collection_count = randint(1, count - 1)
            wishlist_count = count - collection_count
            albums += [create_album(True) for _ in range(collection_count)]
            albums += [create_album(False) for _ in range(wishlist_count)]
        else:
            albums += [create_album(owned) for _ in range(count)]
        return albums

    return create_albums


@pytest.fixture
def form_data_factory():
    def make_form_data(**kwargs):
        default_form_data = {
            "title": random_string(),
            "artist": random_string(),
            "genre": random_user_genre(),
            "pub_date": present_date(),
            "user_rating": random_user_rating(),
        }
        if kwargs is not None:
            default_form_data.update(kwargs)
            return default_form_data
        return default_form_data

    return make_form_data
