from django.urls import reverse
from django.contrib.auth.models import User as AuthUser

from random import choice, randint

from .base import AuthenticatedDomainUserTestCase
from .factories import AlbumFactoryMixin
from .utils import future_date, present_date
from ..urls import app_name
from ..forms.album_forms import AlbumCollectionForm, AlbumWishlistForm
from ..domain.models import Album


class TestCollectionView(AlbumFactoryMixin, AuthenticatedDomainUserTestCase):
    def test_results_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse(f"{app_name}:collection"))
        self.assertRedirects(response, f"/accounts/login/?next=/{app_name}/collection/")

    def test_results_view_no_albums_in_collection(self):
        # When
        response = self.client.get(reverse(f"{app_name}:collection"))
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No albums in your collection yet.")
        self.assertQuerySetEqual(response.context["albums_in_collection"], set())

    def test_results_view_when_albums_in_collection(self):
        albums_in_collection = self.create_albums(owned=True)
        # When
        response = self.client.get(reverse(f"{app_name}:collection"))
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(response.context["albums_in_collection"]), set(albums_in_collection)
        )

    #TODO refactor whole test suites to make use of pytest fixtures for auth user and test parametrization

    def test_search_when_search_query_blank(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        # When
        response = self.client.get(reverse(f"{app_name}:collection"), {"query": ""})
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(response.context["albums_in_collection"]), set(albums_in_collection)
        )

    def test_search_when_albums_in_collection_by_title(self):
        # Given
        self.create_albums(owned=True)
        album_for_search = self.create_album(
            title="Rust In Peace", 
            artist="Megadeth",
            owned=True
        )
        # When
        response = self.client.get(reverse(f"{app_name}:collection"), {"query": album_for_search.title})
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [album for album in response.context["albums_in_collection"]], [album_for_search]
        )

    def test_search_when_albums_in_collection_by_artist(self):
        # Given
        self.create_albums(owned=True)
        album_for_search = self.create_album(
            title="Rust In Peace", 
            artist="Megadeth",
            owned=True
        )
        # When
        response = self.client.get(reverse(f"{app_name}:collection"), {"query": album_for_search.artist})
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [album for album in response.context["albums_in_collection"]], [album_for_search]
        )


class TestDetailView(AlbumFactoryMixin, AuthenticatedDomainUserTestCase):
    def test_detail_view_requires_login(self):
        self.client.logout()
        album_pk = randint(1, 10)
        response = self.client.get(reverse(f"{app_name}:detail", args=[album_pk]))
        self.assertRedirects(response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/")

    def test_detail_view_album_in_collection(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        chosen_album = choice(albums_in_collection)
        # When
        response = self.client.get(
            reverse(f"{app_name}:detail", args=[chosen_album.pk])
        )
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["album"], chosen_album)

    def test_detail_view_album_not_in_collection(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        # When
        response = self.client.get(
            reverse(f"{app_name}:detail", args=[len(albums_in_collection) + 1])
        )
        # Then
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("album", response.context)

    def test_detail_view_album_on_wishlist(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        chosen_album = choice(albums_on_wishlist)
        # When
        response = self.client.get(
            reverse(f"{app_name}:detail", args=[chosen_album.pk])
        )
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["album"], chosen_album)

    def test_detail_view_album_from_different_user(self):
        # Given
        different_user = AuthUser.objects.create_user(
            username="different", password="different"
        )
        albums_in_collection = self.create_albums(
            owned=True, user=different_user.albumz_user
        )
        chosen_album = choice(albums_in_collection)
        # When
        response = self.client.get(
            reverse(f"{app_name}:detail", args=[chosen_album.pk])
        )
        # Then
        self.assertEqual(response.status_code, 404)


class TestWishlistView(AlbumFactoryMixin, AuthenticatedDomainUserTestCase):
    def test_wishlist_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse(f"{app_name}:wishlist"))
        self.assertRedirects(response, f"/accounts/login/?next=/{app_name}/wishlist/")

    def test_wishlist_view_no_albums_on_wishlist(self):
        # When
        response = self.client.get(reverse(f"{app_name}:wishlist"))
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No albums on your wishlist yet.")
        self.assertQuerySetEqual(response.context["albums_on_wishlist"], set())

    def test_wishlist_view_when_albums_on_wishlist(self):
        albums_on_wishlist = self.create_albums(owned=False)
        # When
        response = self.client.get(reverse(f"{app_name}:wishlist"))
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(response.context["albums_on_wishlist"]), set(albums_on_wishlist)
        )

    #TODO refactor whole test suites to make use of pytest fixtures for auth user and test parametrization

    def test_search_when_search_query_blank(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        # When
        response = self.client.get(reverse(f"{app_name}:wishlist"), {"query": ""})
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(response.context["albums_on_wishlist"]), set(albums_on_wishlist)
        )

    def test_search_when_albums_on_wishlist_by_title(self):
        # Given
        self.create_albums(owned=False)
        album_for_search = self.create_album(
            title="Rust In Peace", 
            artist="Megadeth",
            owned=False
        )
        # When
        response = self.client.get(reverse(f"{app_name}:wishlist"), {"query": album_for_search.title})
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [album for album in response.context["albums_on_wishlist"]], [album_for_search]
        )

    def test_search_when_albums_on_wishlist_by_artist(self):
        # Given
        self.create_albums(owned=False)
        album_for_search = self.create_album(
            title="Rust In Peace", 
            artist="Megadeth",
            owned=False
        )
        # When
        response = self.client.get(reverse(f"{app_name}:wishlist"), {"query": album_for_search.artist})
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [album for album in response.context["albums_on_wishlist"]], [album_for_search]
        )


class TestAddAlbumCollectionView(AlbumFactoryMixin, AuthenticatedDomainUserTestCase):
    def test_add_album_collection_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse(f"{app_name}:add_collection"))
        self.assertRedirects(
            response, f"/accounts/login/?next=/{app_name}/collection/add/"
        )

    def test_add_album_collection_get_empty_form(self):
        # When
        response = self.client.get(reverse(f"{app_name}:add_collection"))
        # Then
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, AlbumCollectionForm)
        self.assertFalse(form.is_bound)
        self.assertSetEqual(set(form.errors), set())

    def test_add_album_collection_success(self):
        # Given
        form_data = {
            "title": "Rust In Peace",
            "artist": "Megadeth",
            "pub_date": "1990-09-24",
            "genre": "ROCK",
            "user_rating": "6",
        }
        # When
        response = self.client.post(
            reverse(f"{app_name}:add_collection"), form_data, follow=True
        )
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse(f"{app_name}:collection"))
        self.assertContains(response, "Rust In Peace")
        self.assertTrue(Album.objects.filter(title="Rust In Peace", owned=True).exists())

    def test_add_album_collection_validation_errors_pub_date(self):
        # Given
        form_data = {
            "title": "Rust In Peace",
            "artist": "Megadeth",
            "pub_date": future_date(),
            "genre": "ROCK",
            "user_rating": "6",
        }
        # When
        response = self.client.post(reverse(f"{app_name}:add_collection"), form_data)
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "albumz_app/forms/album_collection_form.html")
        form = response.context["form"]
        errors = form.errors.get("pub_date", [])
        self.assertIn("Publication date cannot be in the future.", errors)
        self.assertTrue(form.is_bound)
        self.assertEqual(form.data["title"], "Rust In Peace")
        self.assertEqual(form.data["artist"], "Megadeth")
        self.assertEqual(form.data["genre"], "ROCK")
        self.assertEqual(form.data["user_rating"], "6")
        self.assertEqual(form.data["pub_date"], future_date().isoformat())

    def test_add_album_collection_album_already_in_collection(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        album_already_in_collection = choice(albums_in_collection)
        form_data = {
            "title": album_already_in_collection.title,
            "artist": album_already_in_collection.artist,
            "pub_date": present_date(),
            "genre": "ROCK",
            "user_rating": "6",
        }
        # When
        response = self.client.post(reverse(f"{app_name}:add_collection"), form_data)
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "albumz_app/forms/album_collection_form.html")
        form = response.context["form"]
        errors = form.non_field_errors()
        self.assertIn("You already own this album!", errors)
        self.assertTrue(form.is_bound)
        self.assertEqual(form.data["title"], album_already_in_collection.title)
        self.assertEqual(form.data["artist"], album_already_in_collection.artist)
        self.assertEqual(form.data["genre"], "ROCK")
        self.assertEqual(form.data["user_rating"], "6")
        self.assertEqual(form.data["pub_date"], present_date().isoformat())


class TestAddAlbumWishlistView(AlbumFactoryMixin, AuthenticatedDomainUserTestCase):
    def test_add_album_wishlist_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse(f"{app_name}:add_wishlist"))
        self.assertRedirects(
            response, f"/accounts/login/?next=/{app_name}/wishlist/add/"
        )

    def test_add_album_wishlist_get_empty_form(self):
        # When
        response = self.client.get(reverse(f"{app_name}:add_wishlist"))
        # Then
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, AlbumWishlistForm)
        self.assertFalse(form.is_bound)
        self.assertSetEqual(set(form.errors), set())

    def test_add_album_wishlist_success(self):
        # Given
        form_data = {
            "title": "Rust In Peace",
            "artist": "Megadeth",
            "pub_date": "1990-09-24",
            "genre": "ROCK",
        }
        # When
        response = self.client.post(
            reverse(f"{app_name}:add_wishlist"), form_data, follow=True
        )
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse(f"{app_name}:wishlist"))
        self.assertContains(response, "Rust In Peace")
        self.assertTrue(Album.objects.filter(title="Rust In Peace", owned=False).exists())

    def test_add_album_wishlist_validation_errors_pub_date(self):
        # Given
        form_data = {
            "title": "Rust In Peace",
            "artist": "Megadeth",
            "pub_date": future_date(),
            "genre": "ROCK",
        }
        # When
        response = self.client.post(reverse(f"{app_name}:add_wishlist"), form_data)
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "albumz_app/forms/album_wishlist_form.html")
        form = response.context["form"]
        errors = form.errors.get("pub_date", [])
        self.assertIn("Publication date cannot be in the future.", errors)
        self.assertTrue(form.is_bound)
        self.assertEqual(form.data["title"], "Rust In Peace")
        self.assertEqual(form.data["artist"], "Megadeth")
        self.assertEqual(form.data["genre"], "ROCK")
        self.assertEqual(form.data["pub_date"], future_date().isoformat())

    def test_add_album_wishlist_album_already_on_wishlist(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        album_already_on_wishlist = choice(albums_on_wishlist)
        form_data = {
            "title": album_already_on_wishlist.title,
            "artist": album_already_on_wishlist.artist,
            "pub_date": present_date(),
            "genre": "ROCK",
        }
        # When
        response = self.client.post(reverse(f"{app_name}:add_wishlist"), form_data)
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "albumz_app/forms/album_wishlist_form.html")
        form = response.context["form"]
        errors = form.non_field_errors()
        self.assertIn("You already have this album on wishlist!", errors)
        self.assertTrue(form.is_bound)
        self.assertEqual(form.data["title"], album_already_on_wishlist.title)
        self.assertEqual(form.data["artist"], album_already_on_wishlist.artist)
        self.assertEqual(form.data["genre"], "ROCK")
        self.assertEqual(form.data["pub_date"], present_date().isoformat())

    def test_add_album_wishlist_album_already_in_collection(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        album_already_in_collection = choice(albums_in_collection)
        form_data = {
            "title": album_already_in_collection.title,
            "artist": album_already_in_collection.artist,
            "pub_date": present_date(),
            "genre": "ROCK",
        }
        # When
        response = self.client.post(reverse(f"{app_name}:add_wishlist"), form_data)
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "albumz_app/forms/album_wishlist_form.html")
        form = response.context["form"]
        errors = form.non_field_errors()
        self.assertIn("You already own this album!", errors)
        self.assertTrue(form.is_bound)
        self.assertEqual(form.data["title"], album_already_in_collection.title)
        self.assertEqual(form.data["artist"], album_already_in_collection.artist)
        self.assertEqual(form.data["genre"], "ROCK")
        self.assertEqual(form.data["pub_date"], present_date().isoformat())


class TestRemoveAlbumView(AlbumFactoryMixin, AuthenticatedDomainUserTestCase):
    def test_remove_album_view_requires_login(self):
        self.client.logout()
        album_pk = randint(1, 10)
        response = self.client.get(reverse(f"{app_name}:delete", args=[album_pk]))
        self.assertRedirects(
            response, f"/accounts/login/?next=/{app_name}/album/{album_pk}/delete"
        )

    def test_remove_album_from_collection_success(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        chosen_album = choice(albums_in_collection)
        # When
        response = self.client.post(reverse(f"{app_name}:delete", args=[chosen_album.pk]), follow=True)
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "albumz_app/collection.html")
        albums_displayed = response.context["albums_in_collection"]
        self.assertNotIn(chosen_album, albums_displayed)

    def test_remove_album_from_wishlist_success(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        chosen_album = choice(albums_on_wishlist)
        # When
        response = self.client.post(reverse(f"{app_name}:delete", args=[chosen_album.pk]), follow=True)
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "albumz_app/wishlist.html")
        albums_displayed = response.context["albums_on_wishlist"]
        self.assertNotIn(chosen_album, albums_displayed)

    def test_remove_album_does_not_exist(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        # When
        response = self.client.post(reverse(f"{app_name}:delete", args=[len(albums_in_collection) + 1]))
        # Then
        self.assertEqual(response.status_code, 404)

    def test_remove_album_different_user(self):
        # Given
        different_user = AuthUser.objects.create_user(
            username="different", password="different"
        )
        albums_in_collection = self.create_albums(owned=True, user=different_user.albumz_user)
        # When
        response = self.client.post(reverse(f"{app_name}:delete", args=[choice(albums_in_collection).pk]))
        # Then
        self.assertEqual(response.status_code, 404)
