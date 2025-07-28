from random import choice

import pytest
from django.urls import reverse
from pytest_django.asserts import (
    assertQuerySetEqual,
    assertRedirects,
    assertTemplateUsed,
)

from ..constants import (
    URLNames,
    ReverseURLNames,
    ResponseStrings,
    TemplateContextVariables,
    DirPaths,
)
from ..forms.album_forms import (
    AlbumCollectionForm,
    AlbumWishlistForm,
)
from ..test_utils.utils import (
    AlbumFiltersMixin,
    AlbumFormMatcherMixin,
    future_date,
    random_positive_number,
)
from ..urls import app_name


class TestCollectionView(AlbumFiltersMixin):
    def test_results_view_requires_login(self, client):
        response = client.get(reverse(ReverseURLNames.COLLECTION))
        assertRedirects(
            response,
            f"/accounts/login/?next=/{app_name}/{URLNames.COLLECTION}/",
        )

    def test_results_view_no_albums_in_collection(self, auth_client):
        # When
        response = auth_client.get(reverse(ReverseURLNames.COLLECTION))
        # Then
        assert response.status_code == 200
        assert ResponseStrings.EMPTY_COLLECTION.encode() in response.content
        assertQuerySetEqual(
            response.context[TemplateContextVariables.ALBUMS_COLLECTION],
            set(),
        )

    def test_results_view_when_albums_in_collection(self, auth_client, albums_factory):
        # Given
        albums = albums_factory(mix=True)
        albums_in_collection = self.filter_albums_by_ownership(True, albums)
        # When
        response = auth_client.get(reverse(ReverseURLNames.COLLECTION))
        # Then
        assert response.status_code == 200
        assert set(response.context[TemplateContextVariables.ALBUMS_COLLECTION]) == set(
            albums_in_collection
        )


class TestDetailView:
    def test_detail_view_requires_login(self, client):
        album_pk = random_positive_number()
        response = client.get(reverse(ReverseURLNames.DETAIL, args=[album_pk]))
        assertRedirects(
            response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/"
        )

    def test_detail_view_album_in_user_albums(self, auth_client, albums_factory):
        # Given
        albums = albums_factory(mix=True)
        chosen_album = choice(albums)
        # When
        response = auth_client.get(
            reverse(ReverseURLNames.DETAIL, args=[chosen_album.pk])
        )
        # Then
        assert response.status_code == 200
        assert response.context[TemplateContextVariables.ALBUM] == chosen_album

    def test_detail_view_album_not_in_user_albums(self, auth_client, albums_factory):
        # Given
        albums = albums_factory(mix=True)
        # When
        response = auth_client.get(
            reverse(ReverseURLNames.DETAIL, args=[len(albums) + 1])
        )
        # Then
        assert response.status_code == 404
        assert TemplateContextVariables.ALBUM not in response.context

    def test_detail_view_album_from_different_user(
        self, auth_client, albums_factory, user_factory
    ):
        # Given
        different_user = user_factory(username="different", password="different")
        albums = albums_factory(mix=True, user=different_user.albumz_user)
        chosen_album = choice(albums)
        # When
        response = auth_client.get(
            reverse(ReverseURLNames.DETAIL, args=[chosen_album.pk])
        )
        # Then
        assert response.status_code == 404


class TestWishlistView(AlbumFiltersMixin):
    def test_wishlist_view_requires_login(self, client):
        response = client.get(reverse(ReverseURLNames.WISHLIST))
        assertRedirects(
            response,
            f"/accounts/login/?next=/{app_name}/{URLNames.WISHLIST}/",
        )

    def test_wishlist_view_no_albums_on_wishlist(self, auth_client):
        # When
        response = auth_client.get(reverse(ReverseURLNames.WISHLIST))
        # Then
        assert response.status_code == 200
        assert ResponseStrings.EMPTY_WISHLIST.encode() in response.content
        assertQuerySetEqual(
            response.context[TemplateContextVariables.ALBUMS_WISHLIST], set()
        )

    def test_wishlist_view_when_albums_on_wishlist(self, auth_client, albums_factory):
        albums = albums_factory(mix=True)
        albums_on_wishlist = self.filter_albums_by_ownership(False, albums)
        # When
        response = auth_client.get(reverse(ReverseURLNames.WISHLIST))
        # Then
        assert response.status_code == 200
        assert set(response.context[TemplateContextVariables.ALBUMS_WISHLIST]) == set(
            albums_on_wishlist
        )


@pytest.mark.parametrize("view", [URLNames.COLLECTION, URLNames.WISHLIST])
class TestSearchView:
    def test_search_by_empty_query(self, view, auth_client, albums_factory):
        # Given
        albums = (
            albums_factory(owned=True)
            if view == URLNames.COLLECTION
            else albums_factory(owned=False)
        )
        # When
        response = auth_client.get(reverse(f"{app_name}:{view}"), {"query": ""})
        # Then
        assert response.status_code == 200
        context_var_name = {
            URLNames.COLLECTION: TemplateContextVariables.ALBUMS_COLLECTION,
            URLNames.WISHLIST: TemplateContextVariables.ALBUMS_WISHLIST,
        }[view]
        assert set(response.context[context_var_name]) == set(albums)

    def test_search_by_title(self, view, auth_client, albums_factory):
        # Given
        albums = (
            albums_factory(owned=True)
            if view == URLNames.COLLECTION
            else albums_factory(owned=False)
        )
        album_for_search = choice(albums)
        # When
        response = auth_client.get(
            reverse(f"{app_name}:{view}"), {"query": album_for_search.title}
        )
        # Then
        assert response.status_code == 200
        context_var_name = {
            URLNames.COLLECTION: TemplateContextVariables.ALBUMS_COLLECTION,
            URLNames.WISHLIST: TemplateContextVariables.ALBUMS_WISHLIST,
        }[view]
        assert album_for_search in [
            album for album in response.context[context_var_name]
        ]

    def test_search_by_artist(self, view, auth_client, albums_factory):
        # Given
        albums = (
            albums_factory(owned=True)
            if view == URLNames.COLLECTION
            else albums_factory(owned=False)
        )
        album_for_search = choice(albums)
        # When
        response = auth_client.get(
            reverse(f"{app_name}:{view}"), {"query": album_for_search.artist}
        )
        # Then
        assert response.status_code == 200
        context_var_name = {
            URLNames.COLLECTION: TemplateContextVariables.ALBUMS_COLLECTION,
            URLNames.WISHLIST: TemplateContextVariables.ALBUMS_WISHLIST,
        }[view]
        assert album_for_search in [
            album for album in response.context[context_var_name]
        ]


class TestAddAlbumCollectionView(AlbumFormMatcherMixin):
    def test_add_album_collection_view_requires_login(self, client):
        response = client.get(reverse(ReverseURLNames.ADD_TO_COLLECTION))
        assertRedirects(
            response,
            f"/accounts/login/?next=/{app_name}/{URLNames.COLLECTION}/add/",
        )

    def test_add_album_collection_get_empty_form(self, auth_client):
        # When
        response = auth_client.get(reverse(ReverseURLNames.ADD_TO_COLLECTION))
        # Then
        assert response.status_code == 200
        form = response.context[TemplateContextVariables.FORM]
        assert type(form) is AlbumCollectionForm
        assert not form.is_bound
        assert set(form.errors) == set()

    def test_add_album_collection_success(self, auth_client, form_data_factory):
        # Given
        form_data = form_data_factory()
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.ADD_TO_COLLECTION), form_data, follow=True
        )
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(ReverseURLNames.COLLECTION))
        assert form_data["title"].encode() in response.content

    def test_add_album_collection_invalid_future_pub_date(
        self, auth_client, form_data_factory
    ):
        # Given
        form_data = form_data_factory(pub_date=future_date())
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.ADD_TO_COLLECTION), form_data
        )
        # Then
        assert response.status_code == 200
        assertTemplateUsed(
            response, DirPaths.FORM_PATH.file("album_creation_form.html")
        )
        form = response.context[TemplateContextVariables.FORM]
        errors = form.errors.get("pub_date", [])
        assert ResponseStrings.PUB_DATE_ERROR in errors
        self.assert_bound_form_matches(form, form_data)

    def test_add_album_collection_album_already_in_collection(
        self, auth_client, albums_factory, form_data_factory
    ):
        # Given
        albums_in_collection = albums_factory(owned=True)
        album_already_in_collection = choice(albums_in_collection)
        form_data = form_data_factory(
            title=album_already_in_collection.title,
            artist=album_already_in_collection.artist,
        )
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.ADD_TO_COLLECTION), form_data
        )
        # Then
        assert response.status_code == 200
        assertTemplateUsed(
            response, DirPaths.FORM_PATH.file("album_creation_form.html")
        )
        form = response.context[TemplateContextVariables.FORM]
        errors = form.non_field_errors()
        assert ResponseStrings.ALBUM_IN_COLLECTION_ERROR in errors
        self.assert_bound_form_matches(form, form_data)

    def test_add_album_collection_album_already_on_wishlist(
        self, auth_client, albums_factory, form_data_factory
    ):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        album_already_on_wishlist = choice(albums_on_wishlist)
        form_data = form_data_factory(
            title=album_already_on_wishlist.title,
            artist=album_already_on_wishlist.artist,
        )
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.ADD_TO_COLLECTION), form_data, follow=True
        )
        assert response.status_code == 200
        assertRedirects(response, reverse(ReverseURLNames.COLLECTION))
        assert form_data["title"].encode() in response.content


class TestAddAlbumWishlistView(AlbumFormMatcherMixin):
    def test_add_album_wishlist_view_requires_login(self, client):
        response = client.get(reverse(ReverseURLNames.ADD_TO_WISHLIST))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/wishlist/add/")

    def test_add_album_wishlist_get_empty_form(self, auth_client):
        # When
        response = auth_client.get(reverse(ReverseURLNames.ADD_TO_WISHLIST))
        # Then
        assert response.status_code == 200
        form = response.context[TemplateContextVariables.FORM]
        assert type(form) is AlbumWishlistForm
        assert not form.is_bound
        assert set(form.errors) == set()

    def test_add_album_wishlist_success(self, auth_client, form_data_factory):
        # Given
        form_data = form_data_factory()
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.ADD_TO_WISHLIST), form_data, follow=True
        )
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(ReverseURLNames.WISHLIST))
        assert form_data["title"].encode() in response.content

    def test_add_album_wishlist_invalid_future_pub_date(
        self, auth_client, form_data_factory
    ):
        # Given
        form_data = form_data_factory(pub_date=future_date())
        # When
        response = auth_client.post(reverse(ReverseURLNames.ADD_TO_WISHLIST), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(
            response, DirPaths.FORM_PATH.file("album_creation_form.html")
        )
        form = response.context[TemplateContextVariables.FORM]
        errors = form.errors.get("pub_date", [])
        assert ResponseStrings.PUB_DATE_ERROR in errors
        self.assert_bound_form_matches(form, form_data)

    def test_add_album_wishlist_album_already_on_wishlist(
        self, auth_client, albums_factory, form_data_factory
    ):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        album_already_on_wishlist = choice(albums_on_wishlist)
        form_data = form_data_factory(
            title=album_already_on_wishlist.title,
            artist=album_already_on_wishlist.artist,
        )
        # When
        response = auth_client.post(reverse(ReverseURLNames.ADD_TO_WISHLIST), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(
            response, DirPaths.FORM_PATH.file("album_creation_form.html")
        )
        form = response.context[TemplateContextVariables.FORM]
        errors = form.non_field_errors()
        assert ResponseStrings.ALBUM_ON_WISHLIST_ERROR in errors
        self.assert_bound_form_matches(form, form_data)

    def test_add_album_wishlist_album_already_in_collection(
        self, auth_client, albums_factory, form_data_factory
    ):
        # Given
        albums_in_collection = albums_factory(owned=True)
        album_already_in_collection = choice(albums_in_collection)
        form_data = form_data_factory(
            title=album_already_in_collection.title,
            artist=album_already_in_collection.artist,
        )
        # When
        response = auth_client.post(reverse(ReverseURLNames.ADD_TO_WISHLIST), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(
            response, DirPaths.FORM_PATH.file("album_creation_form.html")
        )
        form = response.context[TemplateContextVariables.FORM]
        errors = form.non_field_errors()
        assert ResponseStrings.ALBUM_IN_COLLECTION_ERROR in errors
        self.assert_bound_form_matches(form, form_data)


class TestRemoveAlbumView:
    def test_remove_album_view_requires_login(self, client):
        album_pk = random_positive_number()
        response = client.get(reverse(ReverseURLNames.DELETE, args=[album_pk]))
        assertRedirects(
            response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/delete/"
        )

    @pytest.mark.parametrize("owned", [True, False])
    def test_remove_album_from_set_success(self, owned, auth_client, albums_factory):
        # Given
        albums = albums_factory(owned=owned)
        chosen_album = choice(albums)
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.DELETE, args=[chosen_album.pk]),
            follow=True,
        )
        # Then
        assert response.status_code == 200
        assertTemplateUsed(
            response,
            DirPaths.TEMPLATES_PATH.file(
                "collection.html" if owned else "wishlist.html"
            ),
        )
        albums_displayed = response.context[
            (
                TemplateContextVariables.ALBUMS_COLLECTION
                if owned
                else TemplateContextVariables.ALBUMS_WISHLIST
            )
        ]
        assert chosen_album not in albums_displayed

    def test_remove_album_does_not_exist(self, auth_client, albums_factory):
        # Given
        albums = albums_factory(mix=True)
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.DELETE, args=[len(albums) + 1])
        )
        # Then
        assert response.status_code == 404

    def test_remove_album_different_user(
        self, auth_client, albums_factory, user_factory
    ):
        # Given
        different_user = user_factory(username="different", password="different")
        albums = albums_factory(mix=True, user=different_user.albumz_user)
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.DELETE, args=[choice(albums).pk])
        )
        # Then
        assert response.status_code == 404


class TestEditAlbumView(AlbumFormMatcherMixin):
    def test_edit_view_requires_login(self, client):
        album_pk = random_positive_number()
        response = client.get(reverse(ReverseURLNames.EDIT, args=[album_pk]))
        assertRedirects(
            response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/edit/"
        )

    def test_edit_view_get(self, auth_client, albums_factory):
        # Given
        albums = albums_factory(mix=True)
        edited_album = choice(albums)
        # When
        response = auth_client.get(
            reverse(ReverseURLNames.EDIT, args=[edited_album.pk])
        )
        # Then
        assert response.status_code == 200
        form = response.context[TemplateContextVariables.FORM]
        self.assert_unbound_form_matches(form, edited_album)

    def test_edit_view_album_does_not_exist(self, auth_client, albums_factory):
        # Given
        albums = albums_factory(mix=True)
        # When
        response = auth_client.get(
            reverse(ReverseURLNames.EDIT, args=[len(albums) + 1])
        )
        # Then
        assert response.status_code == 404

    def test_edit_view_album_from_different_user(
        self, auth_client, albums_factory, user_factory
    ):
        # Given
        different_user = user_factory(username="test", password="test")
        albums_of_different_user = albums_factory(
            mix=True, user=different_user.albumz_user
        )
        # When
        response = auth_client.get(
            reverse(
                ReverseURLNames.EDIT,
                args=[choice(albums_of_different_user).pk],
            )
        )
        # Then
        assert response.status_code == 404

    @pytest.mark.parametrize("view", [URLNames.COLLECTION, URLNames.WISHLIST])
    def test_edit_view_success(
        self, view, auth_client, albums_factory, form_data_factory
    ):
        # Given
        owned = True if view == URLNames.COLLECTION else False
        albums = albums_factory(owned=owned)
        edited_album = choice(albums)
        update_form_data = form_data_factory()
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.EDIT, args=[edited_album.pk]),
            update_form_data,
            follow=True,
        )
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(f"{app_name}:{view}"))
        assert update_form_data["title"] in response.content.decode()

    @pytest.mark.parametrize("view", [URLNames.COLLECTION, URLNames.WISHLIST])
    def test_edit_view_success_same_title_and_artist(
        self, view, auth_client, albums_factory, form_data_factory
    ):
        # Given
        owned = True if view == URLNames.COLLECTION else False
        albums = albums_factory(owned=owned)
        edited_album = choice(albums)
        update_form_data = form_data_factory(
            title=edited_album.title,
            artist=edited_album.artist,
        )
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.EDIT, args=[edited_album.pk]),
            update_form_data,
            follow=True,
        )
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(f"{app_name}:{view}"))
        assert update_form_data["title"] in response.content.decode()

    @pytest.mark.parametrize("owned", [True, False])
    def test_edit_view_duplicate_album_from_different_set(
        self, owned, auth_client, albums_factory, form_data_factory
    ):
        # Given
        different_set = False if owned else True
        albums = albums_factory(owned=owned)
        albums_from_different_set = albums_factory(owned=different_set)
        edited_album = choice(albums)
        other_album = choice(albums_from_different_set)
        update_form_data = form_data_factory(
            title=other_album.title,
            artist=other_album.artist,
            pub_date=edited_album.pub_date,
            genre=edited_album.genre,
            user_rating=edited_album.user_rating,
            owned=edited_album.owned,
        )
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.EDIT, args=[edited_album.pk]),
            update_form_data,
        )
        # Then
        assert response.status_code == 200
        form = response.context[TemplateContextVariables.FORM]
        errors = form.non_field_errors()
        error_response = (
            ResponseStrings.ALBUM_IN_COLLECTION_ERROR
            if different_set
            else ResponseStrings.ALBUM_ON_WISHLIST_ERROR
        )
        assert error_response in errors
        self.assert_bound_form_matches(form, update_form_data)

    @pytest.mark.parametrize("owned", [True, False])
    def test_edit_view_duplicate_album_from_the_same_set(
        self, owned, auth_client, albums_factory, form_data_factory
    ):
        # Given
        albums = albums_factory(owned=owned)
        edited_album = choice(albums)
        other_album = choice(albums)
        while other_album == edited_album:
            other_album = choice(albums)
        update_form_data = form_data_factory(
            title=other_album.title,
            artist=other_album.artist,
            pub_date=edited_album.pub_date,
            genre=edited_album.genre,
            user_rating=edited_album.user_rating,
            owned=edited_album.owned,
        )
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.EDIT, args=[edited_album.pk]),
            update_form_data,
        )
        # Then
        assert response.status_code == 200
        form = response.context[TemplateContextVariables.FORM]
        errors = form.non_field_errors()
        error_response = (
            ResponseStrings.ALBUM_IN_COLLECTION_ERROR
            if owned
            else ResponseStrings.ALBUM_ON_WISHLIST_ERROR
        )
        assert error_response in errors
        self.assert_bound_form_matches(form, update_form_data)

    @pytest.mark.parametrize("owned", [True, False])
    def test_edit_view_invalid_future_pub_date(
        self, owned, auth_client, albums_factory, form_data_factory
    ):
        # Given
        albums = albums_factory(owned=owned)
        edited_album = choice(albums)
        update_form_data = form_data_factory(
            title=edited_album.title,
            artist=edited_album.artist,
            pub_date=future_date(),
            genre=edited_album.genre,
            user_rating=edited_album.user_rating,
        )
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.EDIT, args=[edited_album.pk]),
            update_form_data,
        )
        # Then
        assert response.status_code == 200
        form = response.context[TemplateContextVariables.FORM]
        errors = form.errors.get("pub_date", [])
        assert ResponseStrings.PUB_DATE_ERROR in errors
        self.assert_bound_form_matches(form, update_form_data)


class TestMoveToCollectionView:
    def test_move_view_requires_login(self, client):
        album_pk = random_positive_number()
        response = client.get(
            reverse(ReverseURLNames.MOVE_TO_COLLECTION, args=[album_pk])
        )
        assertRedirects(
            response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/move/"
        )

    def test_move_view_success(self, auth_client, albums_factory):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        chosen_album = choice(albums_on_wishlist)
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.MOVE_TO_COLLECTION, args=[chosen_album.pk]),
            follow=True,
        )
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(ReverseURLNames.COLLECTION))
        albums_displayed = response.context[TemplateContextVariables.ALBUMS_COLLECTION]
        assert chosen_album in albums_displayed

    def test_move_view_album_already_in_collection(self, auth_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        chosen_album = choice(albums_in_collection)
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.MOVE_TO_COLLECTION, args=[chosen_album.pk]),
            follow=True,
        )
        # Then
        assert response.status_code == 200
        assertRedirects(
            response, reverse(ReverseURLNames.DETAIL, args=(chosen_album.pk,))
        )
        album_displayed = response.context[TemplateContextVariables.ALBUM]
        assert chosen_album == album_displayed

    def test_move_view_album_does_not_exist(self, auth_client):
        # When
        response = auth_client.post(
            reverse(
                ReverseURLNames.MOVE_TO_COLLECTION,
                args=[random_positive_number()],
            )
        )
        # Then
        assert response.status_code == 404

    def test_move_view_album_from_different_user(
        self, auth_client, albums_factory, user_factory
    ):
        # Given
        different_user = user_factory(username="test", password="test")
        albums_from_different_user = albums_factory(
            mix=True, user=different_user.albumz_user
        )
        chosen_album = choice(albums_from_different_user)
        # When
        response = auth_client.post(
            reverse(ReverseURLNames.MOVE_TO_COLLECTION, args=[chosen_album.pk])
        )
        # Then
        assert response.status_code == 404
