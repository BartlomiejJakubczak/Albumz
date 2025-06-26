from django.test import TestCase
from django.contrib.auth.models import User as AuthUser

from random import randint, choice
from datetime import date

from .utils import AlbumTestHelpers, future_date, present_date
from ..domain.models import Album
from ..domain.exceptions import (
    AlbumAlreadyOnWishlistError,
    AlbumAlreadyOwnedError,
    AlbumDoesNotExistError,
)


class TestAlbumModel(TestCase):
    def album_instance(self, title, artist, owned=None):
        return Album(
            title=title,
            artist=artist,
            user=None,
            owned=owned,
        )

    def test_album_on_wishlist(self):
        album = self.album_instance("Rust In Peace", "Megadeth", False)
        self.assertTrue(album.is_on_wishlist())
        self.assertFalse(album.is_in_collection())

    def test_album_in_collection(self):
        album = self.album_instance("Rust In Peace", "Megadeth", True)
        self.assertTrue(album.is_in_collection())
        self.assertFalse(album.is_on_wishlist())

    def test_album_equal_to_another_album(self):
        title = "Rust In Peace"
        artist = "Megadeth"
        self.assertEqual(
            self.album_instance(title, artist),
            self.album_instance(title, artist),
        )

    def test_album_not_equal_to_another_album(self):
        title = "Rust In Peace"
        artist = "Megadeth"
        self.assertNotEqual(
            self.album_instance(title, artist),
            self.album_instance(title, "Metallica"),
        )
        self.assertNotEqual(
            self.album_instance(title, artist),
            self.album_instance("Kill 'Em All", artist),
        )

    def test_album_valid_pub_date_past(self):
        album = self.album_instance("Rust In Peace", "Megadeth")
        album.pub_date = date(1991, 9, 21)
        self.assertTrue(album.is_pub_date_valid())

    def test_album_valid_pub_date_now(self):
        album = self.album_instance("Rust In Peace", "Megadeth")
        album.pub_date = present_date()
        self.assertTrue(album.is_pub_date_valid())

    def test_album_valid_pub_date_none(self):
        album = self.album_instance("Rust In Peace", "Megadeth")
        album.pub_date = None
        self.assertTrue(album.is_pub_date_valid())

    def test_album_invalid_pub_date_future(self):
        album = self.album_instance("Rust In Peace", "Megadeth")
        album.pub_date = future_date()
        self.assertFalse(album.is_pub_date_valid())    


class TestUserModel(AlbumTestHelpers, TestCase):
    @classmethod
    def setUpTestData(cls):
        auth_user = AuthUser.objects.create_user("testuser")
        cls.domain_user = auth_user.albumz_user

    def album_from_form(self, title, artist):
        return Album(
            title=title,
            artist=artist,
            user=None,
            owned=None,
        )

    def get_albums_in_collection(self):
        albums = self.domain_user.albums.all()  # user.albums is the object manager
        albums_in_collection = filter(lambda album: album.owned == True, albums)
        return set(album for album in albums_in_collection)

    def get_albums_on_wishlist(self):
        albums = self.domain_user.albums.all()  # user.albums is the object manager
        albums_on_wishlist = filter(lambda album: album.owned == False, albums)
        return set(album for album in albums_on_wishlist)

    def test_new_user_has_an_empty_wishlist(self):
        # When/Then
        self.assertEqual(len(self.get_albums_on_wishlist()), 0)

    def test_new_user_has_an_empty_collection(self):
        # When/Then
        self.assertEqual(len(self.get_albums_in_collection()), 0)

    def test_get_collection_empty_collection(self):
        # Given
        self.create_albums(owned=False)
        # When
        albums_in_collection = self.domain_user.get_collection()
        # Then
        self.assertEqual(
            len(albums_in_collection), len(self.get_albums_in_collection())
        )
        self.assertSetEqual(
            set(albums_in_collection), set(self.get_albums_in_collection())
        )

    def test_get_collection_albums_in_collection(self):
        # Given
        self.create_albums(owned=True)
        self.create_albums(owned=False)
        # When
        received_albums = self.domain_user.get_collection()
        # Then
        self.assertEqual(len(received_albums), len(self.get_albums_in_collection()))
        self.assertSetEqual(set(received_albums), set(self.get_albums_in_collection()))

    def test_add_to_collection_when_album_already_in_collection(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        album_already_in_collection = choice(albums_in_collection)
        album_from_form = self.album_from_form(
            album_already_in_collection.title, album_already_in_collection.artist
        )
        # When
        with self.assertRaises(AlbumAlreadyOwnedError):
            self.domain_user.add_to_collection(album_from_form)
        # Then
        self.assertEqual(
            len(self.get_albums_in_collection()), len(albums_in_collection)
        )
        self.assertSetEqual(
            set(albums_in_collection), set(self.get_albums_in_collection())
        )

    def test_add_to_collection_when_album_not_in_collection_and_not_on_wishlist(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        albums_on_wishlist = self.create_albums(owned=False)
        album_from_form = self.album_from_form(
            "DefinitelyNotInCollection", "DefinitelyNotInCollectionArtist"
        )
        # When
        self.domain_user.add_to_collection(album_from_form)
        # Then
        self.assertEqual(
            len(self.get_albums_in_collection()), len(albums_in_collection) + 1
        )
        self.assertEqual(len(self.get_albums_on_wishlist()), len(albums_on_wishlist))
        self.assertIn(album_from_form, self.get_albums_in_collection())

    def test_add_to_collection_when_album_on_wishlist(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        album_on_wishlist = choice(albums_on_wishlist)
        album_from_form = self.album_from_form(
            album_on_wishlist.title, album_on_wishlist.artist
        )
        # When
        self.domain_user.add_to_collection(album_from_form)
        # Then
        self.assertEqual(len(self.get_albums_in_collection()), 1)
        self.assertIn(album_from_form, self.get_albums_in_collection())
        self.assertEqual(
            len(self.get_albums_on_wishlist()), len(albums_on_wishlist) - 1
        )
        self.assertNotIn(album_on_wishlist, self.get_albums_on_wishlist())

    def test_add_to_wishlist_when_not_on_wishlist(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        album_from_form = self.album_from_form(
            "DefinitelyNotInCollection", "DefinitelyNotInCollectionArtist"
        )
        # When
        self.domain_user.add_to_wishlist(album_from_form)
        # Then
        self.assertEqual(
            len(self.get_albums_on_wishlist()), len(albums_on_wishlist) + 1
        )
        self.assertIn(album_from_form, self.get_albums_on_wishlist())

    def test_add_to_wishlist_when_already_on_wishlist(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        album_on_wishlist = choice(albums_on_wishlist)
        album_from_form = self.album_from_form(
            album_on_wishlist.title, album_on_wishlist.artist
        )
        # When/Then
        with self.assertRaises(AlbumAlreadyOnWishlistError):
            self.domain_user.add_to_wishlist(album_from_form)
        self.assertEqual(len(self.get_albums_on_wishlist()), len(albums_on_wishlist))
        self.assertIn(album_on_wishlist, self.get_albums_on_wishlist())

    def test_add_to_wishlist_when_album_already_in_collection(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        albums_in_collection = self.create_albums(owned=True)
        album_in_collection = choice(albums_in_collection)
        album_from_form = self.album_from_form(
            album_in_collection.title, album_in_collection.artist
        )
        # When/Then
        with self.assertRaises(AlbumAlreadyOwnedError):
            self.domain_user.add_to_wishlist(album_from_form)
        self.assertEqual(len(self.get_albums_on_wishlist()), len(albums_on_wishlist))
        self.assertNotIn(album_from_form, self.get_albums_on_wishlist())

    def test_remove_from_collection_when_album_already_in_collection(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        album_in_collection = choice(albums_in_collection)
        # When
        self.domain_user.remove_from_collection(album_in_collection.pk)
        # Then
        self.assertEqual(
            len(self.get_albums_in_collection()), len(albums_in_collection) - 1
        )
        self.assertNotIn(album_in_collection, self.get_albums_in_collection())

    def test_remove_from_collection_when_album_not_in_collection(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        # When/Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.domain_user.remove_from_collection(len(albums_in_collection) + 1)
        self.assertEqual(
            len(self.get_albums_in_collection()), len(albums_in_collection)
        )

    def test_remove_from_collection_when_album_not_in_collection_empty_collection(self):
        # When/Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.domain_user.remove_from_collection(randint(1, 10))
        self.assertEqual(len(self.get_albums_in_collection()), 0)

    def test_remove_from_wishlist_when_album_on_wishlist(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        album_on_wishlist = choice(albums_on_wishlist)
        # When
        self.domain_user.remove_from_wishlist(album_on_wishlist.pk)
        # Then
        self.assertEqual(
            len(self.get_albums_on_wishlist()), len(albums_on_wishlist) - 1
        )
        self.assertNotIn(album_on_wishlist, self.get_albums_on_wishlist())

    def test_remove_from_wishlist_when_album_not_on_wishlist(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        # When
        with self.assertRaises(AlbumDoesNotExistError):
            self.domain_user.remove_from_wishlist(len(albums_on_wishlist) + 1)
        self.assertEqual(len(self.get_albums_on_wishlist()), len(albums_on_wishlist))

    def test_remove_from_collection_when_album_not_in_wishlist_empty_wishlist(self):
        # When/Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.domain_user.remove_from_wishlist(randint(1, 10))
        self.assertEqual(len(self.get_albums_on_wishlist()), 0)

    def test_get_album_when_album_in_collection(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        album_in_collection = choice(albums_in_collection)
        # When
        album_from_collection = self.domain_user.get_album(album_in_collection.pk)
        # Then
        self.assertEqual(album_in_collection.pk, album_from_collection.pk)

    def test_get_album_when_album_not_in_collection(self):
        # Given
        albums_in_collection = self.create_albums(owned=True)
        # When/Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.domain_user.get_album(len(albums_in_collection) + 1)

    def test_get_album_when_album_on_wishlist(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        album_on_wishlist = choice(albums_on_wishlist)
        # When
        album_from_wishlist = self.domain_user.get_album(album_on_wishlist.pk)
        # Then
        self.assertEqual(album_from_wishlist.pk, album_from_wishlist.pk)

    def test_get_album_when_album_not_on_wishlist(self):
        # Given
        albums_on_wishlist = self.create_albums(owned=False)
        # When/Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.domain_user.get_album(len(albums_on_wishlist) + 1)
