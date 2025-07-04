import pytest

from .utils import present_date, future_date, random_user_rating
from ..forms.album_forms import (
    AlbumCollectionForm, 
    AlbumWishlistForm,
    AlbumSearchForm
)

def make_form_data(**kwargs):
    default_form_data = {
        "title": "Rust In Peace",
        "artist": "Megadeth",
        "genre": "ROCK",
        "user_rating": random_user_rating(),
    }
    if kwargs is not None:
        default_form_data.update(kwargs)
        return default_form_data
    return default_form_data


class TestAlbumCollectionForm:
    @pytest.mark.parametrize(
            "form_data",
            [
                make_form_data(pub_date="1990-09-24"), # All fields
                make_form_data(), # minimal data
                make_form_data(pub_date=present_date()) # present date
            ]
    )
    def test_valid_form(self, form_data):
        # When
        form = AlbumCollectionForm(form_data)
        # Then
        assert form.is_valid()

    @pytest.mark.parametrize(
            "form_data",
            [
                make_form_data(pub_date=future_date()), # future date
            ]
    )
    def test_invalid_form(self, form_data):
        # When
        form = AlbumCollectionForm(form_data)
        # Then
        assert not form.is_valid()
        assert "pub_date" in form.errors


class TestAlbumWishlistForm:
    @pytest.mark.parametrize(
            "form_data",
            [
                make_form_data(pub_date="1990-09-24"), # All fields
                make_form_data(), # minimal data
                make_form_data(pub_date=present_date()) # present date
            ]
    )
    def test_valid_form(self, form_data):
        # When
        form = AlbumWishlistForm(form_data)
        # Then
        assert form.is_valid()

    @pytest.mark.parametrize(
            "form_data",
            [
                make_form_data(pub_date=future_date()),
            ]
    )
    def test_invalid_form(self, form_data):
        # When
        form = AlbumWishlistForm(form_data)
        # Then
        assert not form.is_valid()
        assert "pub_date" in form.errors


class TestAlbumSearchForm:
    @pytest.mark.parametrize(
            "input_value", 
            ["", "megadeth", "meg", " megadeth "]
    )
    def test_form_accepts_inputs(self, input_value):
        # Given
        form_data = {
            "query": input_value
        }
        # When
        form = AlbumSearchForm(form_data)
        # Then
        assert form.is_valid()