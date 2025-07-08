import pytest

from .utils import (
    present_date, 
    future_date,
)
from ..forms.album_forms import (
    AlbumCollectionForm, 
    AlbumWishlistForm,
    AlbumSearchForm,
    AlbumUpdateForm,
)

class TestAlbumUpdateForm:
    @pytest.mark.parametrize(
            "overrides",
            [
                {"pub_date":"1990-09-24"}, # past date
                {"pub_date":present_date().isoformat()} # present date
            ]
    )
    def test_valid_form(self, overrides, form_data_factory):
        # Given
        form_data = form_data_factory(**overrides)
        # When
        form = AlbumUpdateForm(form_data)
        # Then
        assert form.is_valid()

    @pytest.mark.parametrize(
            "overrides",
            [
                {"pub_date":future_date().isoformat()}, # future date
            ]
    )
    def test_invalid_form(self, overrides, form_data_factory):
        # Given
        form_data = form_data_factory(**overrides)
        # When
        form = AlbumUpdateForm(form_data)
        # Then
        assert not form.is_valid()
        assert "pub_date" in form.errors


class TestAlbumCollectionForm:
    @pytest.mark.parametrize(
            "overrides",
            [
                {"pub_date":"1990-09-24"}, # past date
                {"pub_date":present_date().isoformat()} # present date
            ]
    )
    def test_valid_form(self, overrides, form_data_factory):
        # Given
        form_data = form_data_factory(**overrides)
        # When
        form = AlbumCollectionForm(form_data)
        # Then
        assert form.is_valid()

    @pytest.mark.parametrize(
            "overrides",
            [
                {"pub_date":future_date().isoformat()}, # future date
            ]
    )
    def test_invalid_form(self, overrides, form_data_factory):
        # Given
        form_data = form_data_factory(**overrides)
        # When
        form = AlbumCollectionForm(form_data)
        # Then
        assert not form.is_valid()
        assert "pub_date" in form.errors


class TestAlbumWishlistForm:
    @pytest.mark.parametrize(
            "overrides",
            [
                {"pub_date":"1990-09-24"}, # past date
                {"pub_date":present_date().isoformat()} # present date
            ]
    )
    def test_valid_form(self, overrides, form_data_factory):
        # Given
        form_data = form_data_factory(**overrides)
        # When
        form = AlbumWishlistForm(form_data)
        # Then
        assert form.is_valid()

    @pytest.mark.parametrize(
            "overrides",
            [
                {"pub_date":future_date().isoformat()}, # future date
            ]
    )
    def test_invalid_form(self, overrides, form_data_factory):
        # Given
        form_data = form_data_factory(**overrides)
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