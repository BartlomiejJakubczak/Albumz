from django.test import TestCase
from django.contrib.auth.models import User as AuthUser
from random import randint

from ..domain.models import Album
from ..domain.exceptions import (
    AlbumAlreadyOnWishlistError,
    AlbumAlreadyOwnedError,
    AlbumDoesNotExistError,
)

class TestAlbumModel(TestCase):
    def album_from_form(self, title, owned):
        return Album(
            title=title, 
            artist="Megadeth", 
            user=None,
            owned=owned,
        )
    
    def test_album_on_wishlist(self):
        album = self.album_from_form("Rust In Peace", False)
        self.assertTrue(album.is_on_wishlist())
        self.assertFalse(album.is_in_collection())

    def test_album_in_collection(self):
        album = self.album_from_form("Rust In Peace", True)
        self.assertTrue(album.is_in_collection())
        self.assertFalse(album.is_on_wishlist())

class TestUserModel(TestCase):
    def setUp(self):
        auth_user = AuthUser.objects.create_user("testuser")
        self.user = auth_user.albumz_user

    def album_from_form(self, title):
        return Album(
            title=title, 
            artist="Megadeth", 
            user=None,
            owned=None,
        )
    
    def create_album_on_wishlist(self, title):
        return Album.objects.create(
            title=title, 
            artist="Megadeth", 
            user=self.user,
            owned=False,
        )
    
    def create_album_in_collection(self, title):
        return Album.objects.create(
            title=title, 
            artist="Megadeth", 
            user=self.user,
            owned=True,
        )

    def get_albums_in_collection(self):
        albums = self.user.albums.all() # uer.albums is the object manager
        albums_in_collection = set(album for album in filter(lambda album: album.owned == True, albums))
        return albums_in_collection
    
    def get_albums_on_wishlist(self):
        albums = self.user.albums.all() # uer.albums is the object manager
        albums_on_wishlist = set(album for album in filter(lambda album: album.owned == False, albums))
        return albums_on_wishlist

    def test_new_user_has_an_empty_wishlist(self):
        # When/Then
        self.assertEqual(len(self.get_albums_on_wishlist()), 0)

    def test_new_user_has_an_empty_collection(self):
        # When/Then
        self.assertEqual(len(self.get_albums_in_collection()), 0)

    def test_add_to_collection_when_album_already_in_collection(self):
        # Given
        album_in_collection = self.create_album_in_collection("Rust In Peace")
        self.assertEqual(len(self.get_albums_in_collection()), 1)
        self.assertIn(album_in_collection, self.get_albums_in_collection())
        album_from_form = self.album_from_form("Rust In Peace")
        # When
        with self.assertRaises(AlbumAlreadyOwnedError):
            self.user.add_to_collection(album_from_form)
        # Then
        self.assertEqual(len(self.get_albums_in_collection()), 1)
        self.assertIn(album_in_collection, self.get_albums_in_collection())

    def test_add_to_collection_when_album_not_in_collection(self):
        # Given
        album_from_form = self.album_from_form("Rust In Peace")
        # When
        self.user.add_to_collection(album_from_form)
        # Then
        self.assertEqual(len(self.get_albums_in_collection()), 1)
        self.assertIn(album_from_form, self.get_albums_in_collection())

    def test_add_to_collection_when_album_on_wishlist(self):
        # Given
        album_on_wishlist = self.create_album_on_wishlist("Rust In Peace")
        self.assertEqual(len(self.get_albums_on_wishlist()), 1)
        self.assertIn(album_on_wishlist, self.get_albums_on_wishlist())
        album_from_form = self.album_from_form("Rust In Peace")
        # When
        self.user.add_to_collection(album_from_form)
        # Then
        self.assertEqual(len(self.get_albums_in_collection()), 1)
        self.assertIn(album_from_form, self.get_albums_in_collection())
        self.assertEqual(len(self.get_albums_on_wishlist()), 0)
        self.assertNotIn(album_on_wishlist, self.get_albums_on_wishlist())

    def test_add_to_wishlist_when_not_on_wishlist(self):
        # Given
        album_from_form = self.album_from_form("Rust In Peace")
        # When
        self.user.add_to_wishlist(album_from_form)
        # Then
        self.assertEqual(len(self.get_albums_on_wishlist()), 1)
        self.assertIn(album_from_form, self.get_albums_on_wishlist())

    def test_add_to_wishlist_when_already_on_wishlist(self):
        # Given
        album_on_wishlist = self.create_album_on_wishlist("Rust In Peace")
        self.assertEqual(len(self.get_albums_on_wishlist()), 1)
        self.assertIn(album_on_wishlist, self.get_albums_on_wishlist())
        album_from_form = self.album_from_form("Rust In Peace")
        # When/Then
        with self.assertRaises(AlbumAlreadyOnWishlistError):
            self.user.add_to_wishlist(album_from_form)
        self.assertEqual(len(self.get_albums_on_wishlist()), 1)
        self.assertIn(album_on_wishlist, self.get_albums_on_wishlist())

    def test_add_to_wishlist_when_album_already_in_collection(self):
        # Given
        album_in_collection = self.create_album_in_collection("Rust In Peace")
        self.assertEqual(len(self.get_albums_in_collection()), 1)
        self.assertIn(album_in_collection, self.get_albums_in_collection())
        album_from_form = self.album_from_form("Rust In Peace")
        # When/Then
        with self.assertRaises(AlbumAlreadyOwnedError):
            self.user.add_to_wishlist(album_from_form)
        self.assertEqual(len(self.get_albums_on_wishlist()), 0)
        self.assertNotIn(album_from_form, self.get_albums_on_wishlist())

    def test_remove_from_collection_when_album_already_in_collection(self):
        # Given
        album_in_collection = self.create_album_in_collection("Rust In Peace")
        self.assertEqual(len(self.get_albums_in_collection()), 1)
        self.assertIn(album_in_collection, self.get_albums_in_collection())
        # When
        self.user.remove_from_collection(album_in_collection.pk)
        # Then
        self.assertEqual(len(self.get_albums_in_collection()), 0)
        self.assertNotIn(album_in_collection, self.get_albums_in_collection())
    
    def test_remove_from_collection_when_album_not_in_collection(self):
        # Given
        album_in_collection = self.create_album_in_collection("Rust In Peace")
        self.assertEqual(len(self.get_albums_in_collection()), 1)
        self.assertIn(album_in_collection, self.get_albums_in_collection())
        # When/Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.user.remove_from_collection(album_in_collection.pk + 1)
        self.assertEqual(len(self.get_albums_in_collection()), 1)
        self.assertIn(album_in_collection, self.get_albums_in_collection())

    def test_remove_from_collection_when_album_not_in_collection_empty_collection(self):
        # When/Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.user.remove_from_collection(randint(1,10))
        self.assertEqual(len(self.get_albums_in_collection()), 0)
  
    def test_remove_from_wishlist_when_album_on_wishlist(self):
        # Given
        album_on_wishlist = self.create_album_on_wishlist("Rust In Peace")
        self.assertEqual(len(self.get_albums_on_wishlist()), 1)
        self.assertIn(album_on_wishlist, self.get_albums_on_wishlist())
        # When
        self.user.remove_from_wishlist(album_on_wishlist.pk)
        # Then
        self.assertEqual(len(self.get_albums_on_wishlist()), 0)
        self.assertNotIn(album_on_wishlist, self.get_albums_on_wishlist())

    def test_remove_from_wishlist_when_album_not_on_wishlist(self):
        # Given
        album_on_wishlist = self.create_album_on_wishlist("Rust In Peace")
        self.assertEqual(len(self.get_albums_on_wishlist()), 1)
        self.assertIn(album_on_wishlist, self.get_albums_on_wishlist())
        # When/Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.user.remove_from_wishlist(album_on_wishlist.pk + 1)
        self.assertEqual(len(self.get_albums_on_wishlist()), 1)
        self.assertIn(album_on_wishlist, self.get_albums_on_wishlist())

    def test_remove_from_collection_when_album_not_in_wishlist_empty_wishlist(self):
        # When/Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.user.remove_from_wishlist(randint(1,10))
        self.assertEqual(len(self.get_albums_on_wishlist()), 0)

    def test_get_collection_when_album_in_collection(self):
        # Given
        album_in_collection = self.create_album_in_collection("Rust In Peace")
        album_on_wishlist_1 = self.create_album_on_wishlist("Youthansia")
        album_on_wishlist_2 = self.create_album_on_wishlist("Countdown To Extinction")
        # When
        albums = self.user.get_collection()
        # Then
        self.assertSetEqual(albums, {album_in_collection})

    def test_get_collection_when_no_albums_in_collection(self):
        # Given
        album_on_wishlist_1 = self.create_album_on_wishlist("Youthansia")
        album_on_wishlist_2 = self.create_album_on_wishlist("Countdown To Extinction")
        # When
        albums = self.user.get_collection()
        # Then
        self.assertSetEqual(albums, set())
