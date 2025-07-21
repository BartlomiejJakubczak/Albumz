import pytest
from django.contrib.auth import get_user_model
from random import randint
from .utils import (
    random_user_rating, 
    random_string, 
    random_user_genre,
    present_date,
)


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
                user.albums.create(
                    title=random_string(),
                    artist=random_string(),
                    genre=random_user_genre(),
                    pub_date=present_date(),
                    user_rating = random_user_rating(),
                    owned=owned,
                )
            )
        return albums_in_collection
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