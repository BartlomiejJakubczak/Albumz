import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertQuerySetEqual, assertTemplateUsed

from random import choice

from .utils import (
    future_date, 
    present_date, 
    random_positive_number, 
    random_string, 
    random_user_rating,
)
from ..urls import app_name
from ..forms.album_forms import AlbumCollectionForm, AlbumWishlistForm
from ..domain.models import Album


class TestCollectionView:
    def test_results_view_requires_login(self, client):
        response = client.get(reverse(f"{app_name}:collection"))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/collection/")

    def test_results_view_no_albums_in_collection(self, authenticated_client):
        # When
        response = authenticated_client.get(reverse(f"{app_name}:collection"))
        # Then
        assert response.status_code == 200
        assert b"No albums in your collection yet." in response.content
        assertQuerySetEqual(response.context["albums_in_collection"], set())

    def test_results_view_when_albums_in_collection(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        # When
        response = authenticated_client.get(reverse(f"{app_name}:collection"))
        # Then
        assert response.status_code == 200
        assert set(response.context["albums_in_collection"]) == set(albums_in_collection)


class TestDetailView:
    def test_detail_view_requires_login(self, client):
        album_pk = random_positive_number()
        response = client.get(reverse(f"{app_name}:detail", args=[album_pk]))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/")

    def test_detail_view_album_in_collection(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        chosen_album = choice(albums_in_collection)
        # When
        response = authenticated_client.get(
            reverse(f"{app_name}:detail", args=[chosen_album.pk])
        )
        # Then
        assert response.status_code == 200
        assert response.context["album"] == chosen_album

    def test_detail_view_album_not_in_collection(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        # When
        response = authenticated_client.get(
            reverse(f"{app_name}:detail", args=[len(albums_in_collection) + 1])
        )
        # Then
        assert response.status_code == 404
        assert "album" not in response.context

    def test_detail_view_album_on_wishlist(self, authenticated_client, albums_factory):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        chosen_album = choice(albums_on_wishlist)
        # When
        response = authenticated_client.get(
            reverse(f"{app_name}:detail", args=[chosen_album.pk])
        )
        # Then
        assert response.status_code == 200
        assert chosen_album == response.context["album"]

    def test_detail_view_album_from_different_user(self, authenticated_client, albums_factory, user_factory):
        # Given
        different_user = user_factory(username="different", password="different")
        albums_in_collection = albums_factory(
            owned=True, user=different_user.albumz_user
        )
        chosen_album = choice(albums_in_collection)
        # When
        response = authenticated_client.get(
            reverse(f"{app_name}:detail", args=[chosen_album.pk])
        )
        # Then
        assert response.status_code == 404


class TestWishlistView:
    def test_wishlist_view_requires_login(self, client):
        response = client.get(reverse(f"{app_name}:wishlist"))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/wishlist/")

    def test_wishlist_view_no_albums_on_wishlist(self, authenticated_client):
        # When
        response = authenticated_client.get(reverse(f"{app_name}:wishlist"))
        # Then
        assert response.status_code == 200
        assert b"No albums on your wishlist yet." in response.content
        assertQuerySetEqual(response.context["albums_on_wishlist"], set())

    def test_wishlist_view_when_albums_on_wishlist(self, authenticated_client, albums_factory):
        albums_on_wishlist = albums_factory(owned=False)
        # When
        response = authenticated_client.get(reverse(f"{app_name}:wishlist"))
        # Then
        assert response.status_code == 200
        assert set(response.context["albums_on_wishlist"]) == set(albums_on_wishlist)
        

@pytest.mark.parametrize("view", ["collection", "wishlist"])
class TestSearchView:
    def test_search_by_empty_query(self, view, authenticated_client, albums_factory):
        # Given
        albums = albums_factory(owned=True) if view == "collection" else albums_factory(owned=False)
        # When
        response = authenticated_client.get(reverse(f"{app_name}:{view}"), {"query": ""})
        # Then
        assert response.status_code == 200
        context_var_name = "albums_in_collection" if view == "collection" else "albums_on_wishlist"
        assert set(response.context[context_var_name]) == set(albums)

    def test_search_by_title(self, view, authenticated_client, albums_factory):
        # Given
        albums = albums_factory(owned=True) if view == "collection" else albums_factory(owned=False)
        album_for_search = choice(albums)
        # When
        response = authenticated_client.get(reverse(f"{app_name}:{view}"), {"query": album_for_search.title})
        # Then
        assert response.status_code == 200
        context_var_name = "albums_in_collection" if view == "collection" else "albums_on_wishlist"
        assert [album for album in response.context[context_var_name]] == [album_for_search]
        
    def test_search_by_artist(self, view, authenticated_client, albums_factory):
        # Given
        albums = albums_factory(owned=True) if view == "collection" else albums_factory(owned=False)
        album_for_search = choice(albums)
        # When
        response = authenticated_client.get(reverse(f"{app_name}:{view}"), {"query": album_for_search.artist})
        # Then
        assert response.status_code == 200
        context_var_name = "albums_in_collection" if view == "collection" else "albums_on_wishlist"
        assert [album for album in response.context[context_var_name]] == [album_for_search]


class TestAddAlbumCollectionView:
    def test_add_album_collection_view_requires_login(self, client):
        response = client.get(reverse(f"{app_name}:add_collection"))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/collection/add/")

    def test_add_album_collection_get_empty_form(self, authenticated_client):
        # When
        response = authenticated_client.get(reverse(f"{app_name}:add_collection"))
        # Then
        assert response.status_code == 200
        form = response.context["form"]
        assert type(form) is AlbumCollectionForm
        assert not form.is_bound
        assert set(form.errors) == set()

    def test_add_album_collection_success(self, authenticated_client):
        # Given
        form_data = {
            "title": random_string(),
            "artist": random_string(),
            "pub_date": present_date(),
            "genre": "ROCK",
            "user_rating": random_user_rating(),
        }
        # When
        response = authenticated_client.post(
            reverse(f"{app_name}:add_collection"), form_data, follow=True
        )
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(f"{app_name}:collection"))
        assert form_data["title"].encode() in response.content
        assert Album.objects.filter(title=form_data["title"], owned=True).exists()

    def test_add_album_collection_validation_errors_pub_date(self, authenticated_client):
        # Given
        form_data = {
            "title": random_string(),
            "artist": random_string(),
            "pub_date": future_date(),
            "genre": "ROCK",
            "user_rating": random_user_rating(),
        }
        # When
        response = authenticated_client.post(reverse(f"{app_name}:add_collection"), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, "albumz_app/forms/album_collection_form.html")
        form = response.context["form"]
        errors = form.errors.get("pub_date", [])
        assert "Publication date cannot be in the future." in errors
        assert form.is_bound
        assert form.data["title"] == form_data["title"]
        assert form.data["artist"] == form_data["artist"]
        assert form.data["genre"] == form_data["genre"]
        assert form.data["user_rating"] == str(form_data["user_rating"])
        assert form.data["pub_date"] == form_data["pub_date"].isoformat()

    def test_add_album_collection_album_already_in_collection(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        album_already_in_collection = choice(albums_in_collection)
        form_data = {
            "title": album_already_in_collection.title,
            "artist": album_already_in_collection.artist,
            "pub_date": present_date(),
            "genre": "ROCK",
            "user_rating": random_user_rating(),
        }
        # When
        response = authenticated_client.post(reverse(f"{app_name}:add_collection"), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, "albumz_app/forms/album_collection_form.html")
        form = response.context["form"]
        errors = form.non_field_errors()
        assert "You already own this album!" in errors
        assert form.is_bound
        assert form.data["title"] == form_data["title"]
        assert form.data["artist"] == form_data["artist"]
        assert form.data["genre"] == form_data["genre"]
        assert form.data["user_rating"] == str(form_data["user_rating"])
        assert form.data["pub_date"] == form_data["pub_date"].isoformat()


class TestAddAlbumWishlistView:
    def test_add_album_wishlist_view_requires_login(self, client):
        response = client.get(reverse(f"{app_name}:add_wishlist"))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/wishlist/add/")

    def test_add_album_wishlist_get_empty_form(self, authenticated_client):
        # When
        response = authenticated_client.get(reverse(f"{app_name}:add_wishlist"))
        # Then
        assert response.status_code == 200
        form = response.context["form"]
        assert type(form) is AlbumWishlistForm
        assert not form.is_bound
        assert set(form.errors) == set()

    def test_add_album_wishlist_success(self, authenticated_client):
        # Given
        form_data = {
            "title": random_string(),
            "artist": random_string(),
            "pub_date": present_date(),
            "genre": "ROCK",
        }
        # When
        response = authenticated_client.post(
            reverse(f"{app_name}:add_wishlist"), form_data, follow=True
        )
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(f"{app_name}:wishlist"))
        assert form_data["title"].encode() in response.content 
        assert Album.objects.filter(title=form_data["title"], owned=False).exists()

    def test_add_album_wishlist_validation_errors_pub_date(self, authenticated_client):
        # Given
        form_data = {
            "title": random_string(),
            "artist": random_string(),
            "pub_date": future_date(),
            "genre": "ROCK",
        }
        # When
        response = authenticated_client.post(reverse(f"{app_name}:add_wishlist"), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, "albumz_app/forms/album_wishlist_form.html")
        form = response.context["form"]
        errors = form.errors.get("pub_date", [])
        assert "Publication date cannot be in the future." in errors
        assert form.is_bound
        assert form.data["title"] == form_data["title"]
        assert form.data["artist"] == form_data["artist"]
        assert form.data["genre"] == form_data["genre"]
        assert form.data["pub_date"] == form_data["pub_date"].isoformat()

    def test_add_album_wishlist_album_already_on_wishlist(self, authenticated_client, albums_factory):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        album_already_on_wishlist = choice(albums_on_wishlist)
        form_data = {
            "title": album_already_on_wishlist.title,
            "artist": album_already_on_wishlist.artist,
            "pub_date": present_date(),
            "genre": "ROCK",
        }
        # When
        response = authenticated_client.post(reverse(f"{app_name}:add_wishlist"), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, "albumz_app/forms/album_wishlist_form.html")
        form = response.context["form"]
        errors = form.non_field_errors()
        assert "You already have this album on wishlist!" in errors
        assert form.is_bound
        assert form.data["title"] == form_data["title"]
        assert form.data["artist"] == form_data["artist"]
        assert form.data["genre"] == form_data["genre"]
        assert form.data["pub_date"] == form_data["pub_date"].isoformat()

    def test_add_album_wishlist_album_already_in_collection(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        album_already_in_collection = choice(albums_in_collection)
        form_data = {
            "title": album_already_in_collection.title,
            "artist": album_already_in_collection.artist,
            "pub_date": present_date(),
            "genre": "ROCK",
        }
        # When
        response = authenticated_client.post(reverse(f"{app_name}:add_wishlist"), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, "albumz_app/forms/album_wishlist_form.html")
        form = response.context["form"]
        errors = form.non_field_errors()
        assert "You already own this album!" in errors 
        assert form.is_bound
        assert form.data["title"] == form_data["title"]
        assert form.data["artist"] == form_data["artist"]
        assert form.data["genre"] == form_data["genre"]
        assert form.data["pub_date"] == form_data["pub_date"].isoformat()


class TestRemoveAlbumView:
    def test_remove_album_view_requires_login(self, client):
        album_pk = random_positive_number()
        response = client.get(reverse(f"{app_name}:delete", args=[album_pk]))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/delete")

    def test_remove_album_from_collection_success(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        chosen_album = choice(albums_in_collection)
        # When
        response = authenticated_client.post(reverse(f"{app_name}:delete", args=[chosen_album.pk]), follow=True)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, "albumz_app/collection.html")
        albums_displayed = response.context["albums_in_collection"]
        assert chosen_album not in albums_displayed

    def test_remove_album_from_wishlist_success(self, authenticated_client, albums_factory):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        chosen_album = choice(albums_on_wishlist)
        # When
        response = authenticated_client.post(reverse(f"{app_name}:delete", args=[chosen_album.pk]), follow=True)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, "albumz_app/wishlist.html")
        albums_displayed = response.context["albums_on_wishlist"]
        assert chosen_album not in albums_displayed

    def test_remove_album_does_not_exist(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        # When
        response = authenticated_client.post(reverse(f"{app_name}:delete", args=[len(albums_in_collection) + 1]))
        # Then
        assert response.status_code == 404

    def test_remove_album_different_user(self, authenticated_client, albums_factory, user_factory):
        # Given
        different_user = user_factory(username="different", password="different")
        albums_in_collection = albums_factory(owned=True, user=different_user.albumz_user)
        # When
        response = authenticated_client.post(reverse(f"{app_name}:delete", args=[choice(albums_in_collection).pk]))
        # Then
        assert response.status_code == 404
