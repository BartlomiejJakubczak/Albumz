from datetime import timedelta
from random import choice, randint
from string import ascii_letters, digits

from django.utils import timezone

from ..domain.models import Genre, Rating


def random_string():
    return "".join(choice(ascii_letters) for _ in range(randint(1, 10)))


def random_user_rating():
    return choice(Rating.choices)[0]


def random_user_genre():
    return choice(Genre.choices)[0]


def future_date():
    return timezone.now().date() + timedelta(days=1)


def present_date():
    return timezone.now().date()


def random_positive_number(length=None):
    if length is None:
        length = randint(1, 10)
    return int("".join((choice(digits) for _ in range(length))))


class AlbumFormMatcherMixin:
    def assert_bound_form_matches(self, form, expected_data):
        assert form.is_bound
        assert form.data["title"] == expected_data["title"]
        assert form.data["artist"] == expected_data["artist"]
        assert form.data["genre"] == expected_data["genre"]
        assert form.data["user_rating"] == str(expected_data["user_rating"])
        assert form.data["pub_date"] == expected_data["pub_date"].isoformat()

    def assert_unbound_form_matches(self, form, expected_album):
        assert not form.is_bound
        assert form.instance.title == expected_album.title
        assert form.instance.artist == expected_album.artist
        assert form.instance.genre == expected_album.genre
        assert form.instance.pub_date == expected_album.pub_date
        assert form.instance.user_rating == expected_album.user_rating


class AlbumFiltersMixin:
    def filter_albums_by_ownership(self, owned, albums):
        return list(filter(lambda album: album.owned == owned, albums))
