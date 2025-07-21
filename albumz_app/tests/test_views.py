import pytest
from django.urls import reverse
from pytest_django.asserts import (
    assertRedirects, 
    assertQuerySetEqual, 
    assertTemplateUsed,
)
from random import choice

from .utils import (
    future_date, 
    random_positive_number, 
    AlbumFormMatcherMixin,
)
from .. import constants
from ..urls import app_name
from ..forms.album_forms import AlbumCollectionForm, AlbumWishlistForm


class TestCollectionView:
    def test_results_view_requires_login(self, client):
        response = client.get(reverse(constants.ReverseURLNames.COLLECTION))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/{constants.URLNames.COLLECTION}/")

    def test_results_view_no_albums_in_collection(self, authenticated_client):
        # When
        response = authenticated_client.get(reverse(constants.ReverseURLNames.COLLECTION))
        # Then
        assert response.status_code == 200
        assert constants.ResponseStrings.EMPTY_COLLECTION.encode() in response.content
        assertQuerySetEqual(response.context[constants.TemplateContextVariables.ALBUMS_COLLECTION], set())

    def test_results_view_when_albums_in_collection(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        # When
        response = authenticated_client.get(reverse(constants.ReverseURLNames.COLLECTION))
        # Then
        assert response.status_code == 200
        assert set(response.context[constants.TemplateContextVariables.ALBUMS_COLLECTION]) == set(albums_in_collection)


class TestDetailView:
    def test_detail_view_requires_login(self, client):
        album_pk = random_positive_number()
        response = client.get(reverse(constants.ReverseURLNames.DETAIL, args=[album_pk]))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/")

    @pytest.mark.parametrize("owned", [True, False])
    def test_detail_view_album_in_user_albums(self, owned, authenticated_client, albums_factory):
        # Given
        albums = albums_factory(owned=owned)
        chosen_album = choice(albums)
        # When
        response = authenticated_client.get(
            reverse(constants.ReverseURLNames.DETAIL, args=[chosen_album.pk])
        )
        # Then
        assert response.status_code == 200
        assert response.context[constants.TemplateContextVariables.ALBUM] == chosen_album

    @pytest.mark.parametrize("owned", [True, False])
    def test_detail_view_album_not_in_collection(self, owned, authenticated_client, albums_factory):
        # Given
        albums = albums_factory(owned=owned)
        # When
        response = authenticated_client.get(
            reverse(constants.ReverseURLNames.DETAIL, args=[len(albums) + 1])
        )
        # Then
        assert response.status_code == 404
        assert constants.TemplateContextVariables.ALBUM not in response.context

    @pytest.mark.parametrize("owned", [True, False])
    def test_detail_view_album_from_different_user(self, owned, authenticated_client, albums_factory, user_factory):
        # Given
        different_user = user_factory(username="different", password="different")
        albums = albums_factory(
            owned=owned, user=different_user.albumz_user
        )
        chosen_album = choice(albums)
        # When
        response = authenticated_client.get(
            reverse(constants.ReverseURLNames.DETAIL, args=[chosen_album.pk])
        )
        # Then
        assert response.status_code == 404


class TestWishlistView:
    def test_wishlist_view_requires_login(self, client):
        response = client.get(reverse(constants.ReverseURLNames.WISHLIST))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/{constants.URLNames.WISHLIST}/")

    def test_wishlist_view_no_albums_on_wishlist(self, authenticated_client):
        # When
        response = authenticated_client.get(reverse(constants.ReverseURLNames.WISHLIST))
        # Then
        assert response.status_code == 200
        assert constants.ResponseStrings.EMPTY_WISHLIST.encode() in response.content
        assertQuerySetEqual(response.context[constants.TemplateContextVariables.ALBUMS_WISHLIST], set())

    def test_wishlist_view_when_albums_on_wishlist(self, authenticated_client, albums_factory):
        albums_on_wishlist = albums_factory(owned=False)
        # When
        response = authenticated_client.get(reverse(constants.ReverseURLNames.WISHLIST))
        # Then
        assert response.status_code == 200
        assert set(response.context[constants.TemplateContextVariables.ALBUMS_WISHLIST]) == set(albums_on_wishlist)
        

@pytest.mark.parametrize("view", [constants.URLNames.COLLECTION, constants.URLNames.WISHLIST])
class TestSearchView:
    def test_search_by_empty_query(self, view, authenticated_client, albums_factory):
        # Given
        albums = albums_factory(owned=True) if view == constants.URLNames.COLLECTION else albums_factory(owned=False)
        # When
        response = authenticated_client.get(reverse(f"{app_name}:{view}"), {"query": ""})
        # Then
        assert response.status_code == 200
        context_var_name = {
            constants.URLNames.COLLECTION: constants.TemplateContextVariables.ALBUMS_COLLECTION,
            constants.URLNames.WISHLIST: constants.TemplateContextVariables.ALBUMS_WISHLIST,
        }[view]
        assert set(response.context[context_var_name]) == set(albums)

    def test_search_by_title(self, view, authenticated_client, albums_factory):
        # Given
        albums = albums_factory(owned=True) if view == constants.URLNames.COLLECTION else albums_factory(owned=False)
        album_for_search = choice(albums)
        # When
        response = authenticated_client.get(reverse(f"{app_name}:{view}"), {"query": album_for_search.title})
        # Then
        assert response.status_code == 200
        context_var_name = {
            constants.URLNames.COLLECTION: constants.TemplateContextVariables.ALBUMS_COLLECTION,
            constants.URLNames.WISHLIST: constants.TemplateContextVariables.ALBUMS_WISHLIST,
        }[view]
        assert album_for_search in [album for album in response.context[context_var_name]]
        
    def test_search_by_artist(self, view, authenticated_client, albums_factory):
        # Given
        albums = albums_factory(owned=True) if view == constants.URLNames.COLLECTION else albums_factory(owned=False)
        album_for_search = choice(albums)
        # When
        response = authenticated_client.get(reverse(f"{app_name}:{view}"), {"query": album_for_search.artist})
        # Then
        assert response.status_code == 200
        context_var_name = {
            constants.URLNames.COLLECTION: constants.TemplateContextVariables.ALBUMS_COLLECTION,
            constants.URLNames.WISHLIST: constants.TemplateContextVariables.ALBUMS_WISHLIST,
        }[view]
        assert album_for_search in [album for album in response.context[context_var_name]]


class TestAddAlbumCollectionView(AlbumFormMatcherMixin):
    def test_add_album_collection_view_requires_login(self, client):
        response = client.get(reverse(constants.ReverseURLNames.ADD_TO_COLLECTION))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/{constants.URLNames.COLLECTION}/add/")

    def test_add_album_collection_get_empty_form(self, authenticated_client):
        # When
        response = authenticated_client.get(reverse(constants.ReverseURLNames.ADD_TO_COLLECTION))
        # Then
        assert response.status_code == 200
        form = response.context[constants.TemplateContextVariables.FORM]
        assert type(form) is AlbumCollectionForm
        assert not form.is_bound
        assert set(form.errors) == set()

    def test_add_album_collection_success(self, authenticated_client, form_data_factory):
        # Given
        form_data = form_data_factory()
        # When
        response = authenticated_client.post(
            reverse(constants.ReverseURLNames.ADD_TO_COLLECTION), form_data, follow=True
        )
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(constants.ReverseURLNames.COLLECTION))
        assert form_data["title"].encode() in response.content

    def test_add_album_collection_validation_errors_pub_date(self, authenticated_client, form_data_factory):
        # Given
        form_data = form_data_factory(pub_date=future_date())
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.ADD_TO_COLLECTION), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, constants.DirPaths.FORM_PATH.file("album_creation_form.html"))
        form = response.context[constants.TemplateContextVariables.FORM]
        errors = form.errors.get("pub_date", [])
        assert constants.ResponseStrings.PUB_DATE_ERROR in errors
        self.assert_bound_form_matches(form, form_data)

    def test_add_album_collection_album_already_in_collection(self, authenticated_client, albums_factory, form_data_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        album_already_in_collection = choice(albums_in_collection)
        form_data = form_data_factory(
            title=album_already_in_collection.title, 
            artist=album_already_in_collection.artist, 
        )
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.ADD_TO_COLLECTION), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, constants.DirPaths.FORM_PATH.file("album_creation_form.html"))
        form = response.context[constants.TemplateContextVariables.FORM]
        errors = form.non_field_errors()
        assert constants.ResponseStrings.ALBUM_IN_COLLECTION_ERROR in errors
        self.assert_bound_form_matches(form, form_data)

    def test_add_album_collection_album_already_on_wishlist(self, authenticated_client, albums_factory, form_data_factory):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        album_already_on_wishlist = choice(albums_on_wishlist)
        form_data = form_data_factory(
            title=album_already_on_wishlist.title, 
            artist=album_already_on_wishlist.artist, 
        )
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.ADD_TO_COLLECTION), form_data, follow=True)
        assert response.status_code == 200
        assertRedirects(response, reverse(constants.ReverseURLNames.COLLECTION))
        assert form_data["title"].encode() in response.content


class TestAddAlbumWishlistView(AlbumFormMatcherMixin):
    def test_add_album_wishlist_view_requires_login(self, client):
        response = client.get(reverse(constants.ReverseURLNames.ADD_TO_WISHLIST))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/wishlist/add/")

    def test_add_album_wishlist_get_empty_form(self, authenticated_client):
        # When
        response = authenticated_client.get(reverse(constants.ReverseURLNames.ADD_TO_WISHLIST))
        # Then
        assert response.status_code == 200
        form = response.context[constants.TemplateContextVariables.FORM]
        assert type(form) is AlbumWishlistForm
        assert not form.is_bound
        assert set(form.errors) == set()

    def test_add_album_wishlist_success(self, authenticated_client, form_data_factory):
        # Given
        form_data = form_data_factory()
        # When
        response = authenticated_client.post(
            reverse(constants.ReverseURLNames.ADD_TO_WISHLIST), form_data, follow=True
        )
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(constants.ReverseURLNames.WISHLIST))
        assert form_data["title"].encode() in response.content 

    def test_add_album_wishlist_validation_errors_pub_date(self, authenticated_client, form_data_factory):
        # Given
        form_data = form_data_factory(pub_date=future_date())
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.ADD_TO_WISHLIST), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, constants.DirPaths.FORM_PATH.file("album_creation_form.html"))
        form = response.context[constants.TemplateContextVariables.FORM]
        errors = form.errors.get("pub_date", [])
        assert constants.ResponseStrings.PUB_DATE_ERROR in errors
        self.assert_bound_form_matches(form, form_data)

    def test_add_album_wishlist_album_already_on_wishlist(self, authenticated_client, albums_factory, form_data_factory):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        album_already_on_wishlist = choice(albums_on_wishlist)
        form_data = form_data_factory(
            title=album_already_on_wishlist.title, 
            artist=album_already_on_wishlist.artist, 
        )
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.ADD_TO_WISHLIST), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, constants.DirPaths.FORM_PATH.file("album_creation_form.html"))
        form = response.context[constants.TemplateContextVariables.FORM]
        errors = form.non_field_errors()
        assert constants.ResponseStrings.ALBUM_ON_WISHLIST_ERROR in errors
        self.assert_bound_form_matches(form, form_data)

    def test_add_album_wishlist_album_already_in_collection(self, authenticated_client, albums_factory, form_data_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        album_already_in_collection = choice(albums_in_collection)
        form_data = form_data_factory(
            title=album_already_in_collection.title, 
            artist=album_already_in_collection.artist,
        )
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.ADD_TO_WISHLIST), form_data)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, constants.DirPaths.FORM_PATH.file("album_creation_form.html"))
        form = response.context[constants.TemplateContextVariables.FORM]
        errors = form.non_field_errors()
        assert constants.ResponseStrings.ALBUM_IN_COLLECTION_ERROR in errors 
        self.assert_bound_form_matches(form, form_data)


class TestRemoveAlbumView:
    def test_remove_album_view_requires_login(self, client):
        album_pk = random_positive_number()
        response = client.get(reverse(constants.ReverseURLNames.DELETE, args=[album_pk]))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/delete/")

    def test_remove_album_from_collection_success(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        chosen_album = choice(albums_in_collection)
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.DELETE, args=[chosen_album.pk]), follow=True)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, constants.DirPaths.TEMPLATES_PATH.file("collection.html"))
        albums_displayed = response.context[constants.TemplateContextVariables.ALBUMS_COLLECTION]
        assert chosen_album not in albums_displayed

    def test_remove_album_from_wishlist_success(self, authenticated_client, albums_factory):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        chosen_album = choice(albums_on_wishlist)
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.DELETE, args=[chosen_album.pk]), follow=True)
        # Then
        assert response.status_code == 200
        assertTemplateUsed(response, constants.DirPaths.TEMPLATES_PATH.file("wishlist.html"))
        albums_displayed = response.context[constants.TemplateContextVariables.ALBUMS_WISHLIST]
        assert chosen_album not in albums_displayed

    def test_remove_album_does_not_exist(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.DELETE, args=[len(albums_in_collection) + 1]))
        # Then
        assert response.status_code == 404

    def test_remove_album_different_user(self, authenticated_client, albums_factory, user_factory):
        # Given
        different_user = user_factory(username="different", password="different")
        albums_in_collection = albums_factory(owned=True, user=different_user.albumz_user)
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.DELETE, args=[choice(albums_in_collection).pk]))
        # Then
        assert response.status_code == 404


class TestEditAlbumView(AlbumFormMatcherMixin):
    def test_edit_view_requires_login(self, client):
        album_pk = random_positive_number()
        response = client.get(reverse(constants.ReverseURLNames.EDIT, args=[album_pk]))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/edit/")

    @pytest.mark.parametrize("view", [constants.URLNames.COLLECTION, constants.URLNames.WISHLIST])
    def test_edit_view_get(self, view, authenticated_client, albums_factory):
        # Given
        albums = albums_factory(owned=True) if view == constants.URLNames.COLLECTION else albums_factory(owned=False)
        edited_album = choice(albums)
        # When
        response = authenticated_client.get(reverse(constants.ReverseURLNames.EDIT, args=[edited_album.pk]))
        # Then
        assert response.status_code == 200
        form = response.context[constants.TemplateContextVariables.FORM]
        self.assert_unbound_form_matches(form, edited_album)

    def test_edit_view_album_does_not_exist(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        albums_on_wishlist = albums_factory(owned=False)
        # When
        response = authenticated_client.get(reverse(constants.ReverseURLNames.EDIT, args=[len(albums_in_collection) + len(albums_on_wishlist) + 1]))
        # Then
        assert response.status_code == 404

    def test_edit_view_album_from_different_user(self, authenticated_client, albums_factory, user_factory):
        # Given
        different_user = user_factory(username="test", password="test")
        albums_of_different_user = albums_factory(owned=True, user=different_user.albumz_user)
        # When
        response = authenticated_client.get(reverse(constants.ReverseURLNames.EDIT, args=[choice(albums_of_different_user).pk]))
        # Then
        assert response.status_code == 404

    @pytest.mark.parametrize("view", [constants.URLNames.COLLECTION, constants.URLNames.WISHLIST])
    def test_edit_view_success(self, view, authenticated_client, albums_factory, form_data_factory):
        # Given
        owned = True if view == constants.URLNames.COLLECTION else False
        albums = albums_factory(owned=owned)
        edited_album = choice(albums)
        update_form_data = form_data_factory()
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.EDIT, args=[edited_album.pk]), update_form_data, follow=True)
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(f"{app_name}:{view}"))
        assert update_form_data["title"] in response.content.decode()

    @pytest.mark.parametrize("view", [constants.URLNames.COLLECTION, constants.URLNames.WISHLIST])
    def test_edit_view_success_same_title_and_artist(self, view, authenticated_client, albums_factory, form_data_factory):
        # Given
        owned = True if view == constants.URLNames.COLLECTION else False
        albums = albums_factory(owned=owned)
        edited_album = choice(albums)
        update_form_data = form_data_factory(
            title=edited_album.title,
            artist=edited_album.artist,
        )
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.EDIT, args=[edited_album.pk]), update_form_data, follow=True)
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(f"{app_name}:{view}"))
        assert update_form_data["title"] in response.content.decode()

    @pytest.mark.parametrize("owned", [True, False])
    def test_edit_view_duplicate_album_from_different_set(self, owned, authenticated_client, albums_factory, form_data_factory):
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
        response = authenticated_client.post(reverse(constants.ReverseURLNames.EDIT, args=[edited_album.pk]), update_form_data)
        # Then
        assert response.status_code == 200
        form = response.context[constants.TemplateContextVariables.FORM]
        errors = form.non_field_errors()
        error_response = constants.ResponseStrings.ALBUM_IN_COLLECTION_ERROR if different_set else constants.ResponseStrings.ALBUM_ON_WISHLIST_ERROR
        assert error_response in errors
        self.assert_bound_form_matches(form, update_form_data)

    @pytest.mark.parametrize("owned", [True, False])
    def test_edit_view_duplicate_album_from_the_same_set(self, owned, authenticated_client, albums_factory, form_data_factory):
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
        response = authenticated_client.post(reverse(constants.ReverseURLNames.EDIT, args=[edited_album.pk]), update_form_data)
        # Then
        assert response.status_code == 200
        form = response.context[constants.TemplateContextVariables.FORM]
        errors = form.non_field_errors()
        error_response = constants.ResponseStrings.ALBUM_IN_COLLECTION_ERROR if owned else constants.ResponseStrings.ALBUM_ON_WISHLIST_ERROR
        assert error_response in errors
        self.assert_bound_form_matches(form, update_form_data)

    @pytest.mark.parametrize("owned", [True, False])
    def test_edit_view_validation_errors_pub_date(self, owned, authenticated_client, albums_factory, form_data_factory):
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
        response = authenticated_client.post(reverse(constants.ReverseURLNames.EDIT, args=[edited_album.pk]), update_form_data)
        # Then
        assert response.status_code == 200
        form = response.context[constants.TemplateContextVariables.FORM]
        errors = form.errors.get("pub_date", [])
        assert constants.ResponseStrings.PUB_DATE_ERROR in errors
        self.assert_bound_form_matches(form, update_form_data)


class TestMoveToCollectionView:
    def test_move_view_requires_login(self, client):
        album_pk = random_positive_number()
        response = client.get(reverse(constants.ReverseURLNames.MOVE_TO_COLLECTION, args=[album_pk]))
        assertRedirects(response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/move/")

    def test_move_view_success(self, authenticated_client, albums_factory):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        chosen_album = choice(albums_on_wishlist)
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.MOVE_TO_COLLECTION, args=[chosen_album.pk]), follow=True)
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(constants.ReverseURLNames.COLLECTION))
        albums_displayed = response.context[constants.TemplateContextVariables.ALBUMS_COLLECTION]
        assert chosen_album in albums_displayed

    def test_move_view_album_already_in_collection(self, authenticated_client, albums_factory):
        # Given
        albums_in_collection = albums_factory(owned=True)
        chosen_album = choice(albums_in_collection)
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.MOVE_TO_COLLECTION, args=[chosen_album.pk]), follow=True)
        # Then
        assert response.status_code == 200
        assertRedirects(response, reverse(constants.ReverseURLNames.DETAIL, args=(chosen_album.pk,)))
        album_displayed = response.context[constants.TemplateContextVariables.ALBUM]
        assert chosen_album == album_displayed

    def test_move_view_album_does_not_exist(self, authenticated_client):
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.MOVE_TO_COLLECTION, args=[random_positive_number()]))
        # Then
        assert response.status_code == 404

    def test_move_view_album_from_different_user(self, authenticated_client, albums_factory, user_factory):
        # Given
        different_user = user_factory(username="test", password="test")
        albums_from_different_user = albums_factory(owned=True, user=different_user.albumz_user)
        chosen_album = choice(albums_from_different_user)
        # When
        response = authenticated_client.post(reverse(constants.ReverseURLNames.MOVE_TO_COLLECTION, args=[chosen_album.pk]))
        # Then
        assert response.status_code == 404
