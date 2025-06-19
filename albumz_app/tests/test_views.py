from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User as AuthUser

from random import choice

from .utils import AlbumTestHelpers
from ..urls import app_name

class TestResultsView(AlbumTestHelpers, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "testuser"
        cls.user = AuthUser.objects.create_user(username="testuser", password=cls.password)
        cls.domain_user = cls.user.albumz_user

    def test_results_view_requires_login(self):
        response = self.client.get(reverse(f"{app_name}:results"))
        self.assertRedirects(response, f'/accounts/login/?next=/{app_name}/results/')

    def test_results_view_no_albums_in_collection(self):
        # Given
        self.client.login(username=self.user.username, password=self.password)
        # need to put in plain text for password, because self.user.password will access the hashed password from database
        # When
        response = self.client.get(reverse(f"{app_name}:results"))
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No albums in your collection yet.")
        self.assertQuerySetEqual(response.context["albums_in_collection"], set())

    def test_results_view_when_albums_in_collection(self):
        # Given
        self.client.login(username=self.user.username, password=self.password)
        albums_in_collection = self.create_albums(owned=True)
        # When
        response = self.client.get(reverse(f"{app_name}:results"))
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(response.context["albums_in_collection"]),
            set(albums_in_collection)
        )
        
class TestDetailView(AlbumTestHelpers, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "testuser"
        cls.user = AuthUser.objects.create_user(username="testuser", password=cls.password)
        cls.domain_user = cls.user.albumz_user
    
    def test_detail_view_requires_login(self):
        response = self.client.get(f'/{app_name}/album/1/')
        self.assertRedirects(response, f'/accounts/login/?next=/{app_name}/album/1/')

    def test_detail_view_album_in_collection(self):
        # Given
        self.client.login(username=self.user.username, password=self.password)
        albums_in_collection = self.create_albums(owned=True)
        chosen_album = choice(albums_in_collection)
        # When
        response = self.client.get(reverse(f"{app_name}:detail", args=[chosen_album.pk]))
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["album"], chosen_album)

    def test_detail_view_album_not_in_collection(self):
        # Given
        self.client.login(username=self.user.username, password=self.password)
        albums_in_collection = self.create_albums(owned=True)
        # When
        response = self.client.get(reverse(f"{app_name}:detail", args=[len(albums_in_collection) + 1]))
        # Then
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("album", response.context)

    def test_detail_view_album_on_wishlist(self):
        # Given
        self.client.login(username=self.user.username, password=self.password)
        albums_on_wishlist = self.create_albums(owned=False)
        chosen_album = choice(albums_on_wishlist)
        # When
        response = self.client.get(reverse(f"{app_name}:detail", args=[chosen_album.pk]))
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["album"], chosen_album)

    def test_detail_view_album_from_different_user(self):
        # Given
        different_user = AuthUser.objects.create_user(username="different", password="different")
        albums_in_collection = self.create_albums(owned=True, user=different_user.albumz_user)
        self.client.login(username=self.user.username, password=self.password)
        chosen_album = choice(albums_in_collection)
        # When
        response = self.client.get(reverse(f"{app_name}:detail", args=[chosen_album.pk]))
        # Then
        self.assertEqual(response.status_code, 404)

class TestWishlistView(AlbumTestHelpers, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "testuser"
        cls.user = AuthUser.objects.create_user(username="testuser", password=cls.password)
        cls.domain_user = cls.user.albumz_user

    def test_wishlist_view_requires_login(self):
        response = self.client.get(reverse(f"{app_name}:wishlist"))
        self.assertRedirects(response, f'/accounts/login/?next=/{app_name}/wishlist/')

    def test_results_view_no_albums_on_wishlist(self):
        # Given
        self.client.login(username=self.user.username, password=self.password)
        # When
        response = self.client.get(reverse(f"{app_name}:wishlist"))
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No albums on your wishlist yet.")
        self.assertQuerySetEqual(response.context["albums_on_wishlist"], set())

    def test_results_view_when_albums_on_wishlist(self):
        # Given
        self.client.login(username=self.user.username, password=self.password)
        albums_on_wishlist = self.create_albums(owned=False)
        # When
        response = self.client.get(reverse(f"{app_name}:wishlist"))
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(response.context["albums_on_wishlist"]),
            set(albums_on_wishlist)
        )
