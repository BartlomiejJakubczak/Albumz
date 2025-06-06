from django.test import TestCase

from ..domain.models import Wishlist, Album, Artist, User
from ..domain.exceptions import (
    AlbumAlreadyOnWishlistError,
    AlbumAlreadyOwnedError,
    AlbumDoesNotExistError,
)

class TestWishlistModel(TestCase):
    def setUp(self):
        self.wishlist = Wishlist.objects.create()
        self.artist = Artist.objects.create(name="Megadeth", country="USA")
        self.album = Album.objects.create(title="Rust In Peace", artist=self.artist)
        
    def test_add_when_album_not_in_wishlist(self):
        # When
        self.wishlist.add(self.album)
        # Then
        self.assertEqual(self.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.wishlist.albums.all())

    def test_add_when_album_already_on_wishlist(self):
        # When
        self.wishlist.add(self.album)
        self.assertEqual(self.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.wishlist.albums.all())
        # Then
        with self.assertRaises(AlbumAlreadyOnWishlistError):
            self.wishlist.add(self.album)
        self.assertEqual(self.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.wishlist.albums.all())

    def test_remove_when_album_exists(self):
        # Given
        self.wishlist.add(self.album)
        self.assertEqual(self.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.wishlist.albums.all())
        # When
        self.wishlist.remove(self.album)
        # Then
        self.assertFalse(self.wishlist.albums.contains(self.album))
        self.assertEqual(self.wishlist.albums.count(), 0)
    
    def test_remove_when_album_not_exists(self):
        # Given
        self.wishlist.add(self.album)
        self.assertEqual(self.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.wishlist.albums.all())
        album_not_on_wishlist = Album.objects.create(title="Youthanasia", artist=self.artist)
        # When/Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.wishlist.remove(album_not_on_wishlist)
        self.assertEqual(self.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.wishlist.albums.all())

class TestAlbumModel(TestCase): ...

class TestUserModel(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        self.artist = Artist.objects.create(name="Megadeth", country="USA")
        self.album = Album.objects.create(title="Rust In Peace", artist=self.artist)

    def test_new_user_has_an_empty_wishlist(self):
        # When/Then
        self.assertTrue(self.user.wishlist)

    def test_add_to_collection_when_album_already_owned(self):
        # Given
        self.assertEqual(self.user.albums.count(), 0)
        self.user.add_to_collection(self.album)
        self.assertEqual(self.user.albums.count(), 1)
        self.assertIn(self.album, self.user.albums.all())
        # When/Then
        with self.assertRaises(AlbumAlreadyOwnedError):
            self.user.add_to_collection(self.album)
        self.assertEqual(self.user.albums.count(), 1)
        self.assertIn(self.album, self.user.albums.all())

    def test_add_to_collection_when_album_not_owned(self):
        # Given
        self.assertEqual(self.user.albums.count(), 0)
        # When
        self.user.add_to_collection(self.album)
        # Then
        self.assertEqual(self.user.albums.count(), 1)
        self.assertIn(self.album, self.user.albums.all())

    def test_add_to_collection_when_album_on_wishlist(self):
        # Given
        self.assertEqual(self.user.albums.count(), 0)
        self.assertEqual(self.user.wishlist.albums.count(), 0)
        self.user.wishlist.add(self.album)
        self.assertEqual(self.user.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.user.wishlist.albums.all())
        # When
        self.user.add_to_collection(self.album)
        # Then
        self.assertEqual(self.user.wishlist.albums.count(), 0)
        self.assertEqual(self.user.albums.count(), 1)
        self.assertIn(self.album, self.user.albums.all())

    def test_add_to_collection_when_album_not_on_wishlist(self):
        # Given
        self.assertEqual(self.user.albums.count(), 0)
        self.assertEqual(self.user.wishlist.albums.count(), 0)
        self.user.wishlist.add(self.album)
        other_album = Album.objects.create(title="Youthanasia", artist=self.artist)
        # When
        self.user.add_to_collection(other_album)
        # Then
        self.assertEqual(self.user.albums.count(), 1)
        self.assertIn(other_album, self.user.albums.all())
        self.assertEqual(self.user.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.user.wishlist.albums.all())

    def test_add_to_wishlist_when_not_on_wishlist(self):
        # Given
        self.assertEqual(self.user.wishlist.albums.count(), 0)
        # When
        self.user.add_to_wishlist(self.album)
        # Then
        self.assertEqual(self.user.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.user.wishlist.albums.all())

    def test_add_to_wishlist_when_already_on_wishlist(self):
        # Given
        self.assertEqual(self.user.wishlist.albums.count(), 0)
        self.user.add_to_wishlist(self.album)
        self.assertEqual(self.user.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.user.wishlist.albums.all())
        # When/Then
        with self.assertRaises(AlbumAlreadyOnWishlistError):
            self.user.add_to_wishlist(self.album)
        self.assertEqual(self.user.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.user.wishlist.albums.all())

    def test_remove_from_collection_when_album_exists(self):
        # Given
        self.assertEqual(self.user.albums.count(), 0)
        self.user.add_to_collection(self.album)
        self.assertEqual(self.user.albums.count(), 1)
        self.assertIn(self.album, self.user.albums.all())
        # When
        self.user.remove_from_collection(self.album)
        # Then
        self.assertEqual(self.user.albums.count(), 0)
        self.assertNotIn(self.album, self.user.albums.all())

    def test_remove_from_collection_when_album_not_exists(self):
        # Given
        self.assertEqual(self.user.albums.count(), 0)
        self.user.add_to_collection(self.album)
        self.assertEqual(self.user.albums.count(), 1)
        self.assertIn(self.album, self.user.albums.all())
        other_album = Album.objects.create(title="Youthanasia", artist=self.artist)
        self.assertNotIn(other_album, self.user.albums.all())
        # When/Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.user.remove_from_collection(other_album)
        self.assertEqual(self.user.albums.count(), 1)
        self.assertIn(self.album, self.user.albums.all())
        
    def test_remove_from_wishlist_when_album_exists(self):
        # Given
        self.assertEqual(self.user.wishlist.albums.count(), 0)
        self.user.add_to_wishlist(self.album)
        self.assertEqual(self.user.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.user.wishlist.albums.all())
        # When
        self.user.remove_from_wishlist(self.album)
        # Then
        self.assertEqual(self.user.wishlist.albums.count(), 0)
        self.assertNotIn(self.album, self.user.wishlist.albums.all())

    def test_remove_from_wishlist_when_album_not_exists(self):
        # Given
        self.assertEqual(self.user.wishlist.albums.count(), 0)
        self.user.add_to_wishlist(self.album)
        self.assertEqual(self.user.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.user.wishlist.albums.all())
        other_album = Album.objects.create(title="Youthanasia", artist=self.artist)
        # When / Then
        with self.assertRaises(AlbumDoesNotExistError):
            self.user.remove_from_wishlist(other_album)
        self.assertEqual(self.user.wishlist.albums.count(), 1)
        self.assertIn(self.album, self.user.wishlist.albums.all())