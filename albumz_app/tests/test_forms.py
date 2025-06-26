from django.test import TestCase

from .utils import present_date, future_date
from ..forms.album_forms import AlbumCollectionForm

class TestAlbumCollectionForm(TestCase):
    def test_valid_form_complete_data(self):
        # Given
        form_data = {
            "title": "Rust In Peace",
            "artist": "Megadeth",
            "pub_date": "1990-09-24",
            "genre": "ROCK",
            "user_rating": "6"
        }
        # When
        form = AlbumCollectionForm(form_data)
        # Then
        self.assertTrue(form.is_valid())

    def test_valid_form_incomplete_data(self):
        # Given
        form_data = {
            "title": "Rust In Peace",
            "artist": "Megadeth",
            "genre": "ROCK",
            "user_rating": "6"
        }
        # When
        form = AlbumCollectionForm(form_data)
        # Then
        self.assertTrue(form.is_valid())

    def test_valid_form_pub_date_now(self):
        # Given
        form_data = {
            "title": "Rust In Peace",
            "artist": "Megadeth",
            "pub_date": present_date(),
            "genre": "ROCK",
            "user_rating": "6"
        }
        # When
        form = AlbumCollectionForm(form_data)
        # Then
        self.assertTrue(form.is_valid())

    def test_invalid_form_pub_date_future(self):
        # Given
        form_data = {
            "title": "Rust In Peace",
            "artist": "Megadeth",
            "pub_date": future_date(),
            "genre": "ROCK",
            "user_rating": "6"
        }
        # When
        form = AlbumCollectionForm(form_data)
        # Then
        self.assertFalse(form.is_valid())
        self.assertIn("pub_date", form.errors)
        self.assertIn("Publication date cannot be in the future.", form.errors["pub_date"])
