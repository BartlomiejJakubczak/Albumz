import pytest

from random import choice
from datetime import date

from .utils import (
    future_date, 
    present_date, 
    random_user_rating,
    random_string,
    random_user_genre,
)
from ..domain.models import Album
from ..domain.exceptions import (
    AlbumAlreadyOnWishlistError,
    AlbumAlreadyInCollectionError,
)


class TestAlbumModel:
    def album_instance(self, title, artist, pub_date=None, owned=None):
        return Album(
            title=title,
            artist=artist,
            user=None,
            pub_date=pub_date,
            owned=owned,
        )

    def test_album_on_wishlist(self):
        album = self.album_instance("Rust In Peace", "Megadeth", owned=False)
        assert album.is_on_wishlist()
        assert not album.is_in_collection()

    def test_album_in_collection(self):
        album = self.album_instance("Rust In Peace", "Megadeth", owned=True)
        assert album.is_in_collection()
        assert not album.is_on_wishlist()

    def test_album_equal_to_another_album(self):
        title = "Rust In Peace"
        artist = "Megadeth"
        assert self.album_instance(title, artist) == self.album_instance(title, artist)

    def test_album_not_equal_to_another_album(self):
        title = "Rust In Peace"
        artist = "Megadeth"
        assert self.album_instance(title, artist) != self.album_instance(title, "Metallica")
        assert self.album_instance(title, artist) != self.album_instance("Kill 'Em All", artist)

    @pytest.mark.parametrize(
            "pub_date", [date(1991, 9, 21), present_date(), None]
    )
    def test_album_valid_pub_date(self, pub_date):
        album = self.album_instance("Rust In Peace", "Megadeth", pub_date=pub_date)
        assert album.is_pub_date_valid()

    def test_album_invalid_pub_date_future(self):
        album = self.album_instance("Rust In Peace", "Megadeth", pub_date=future_date())
        assert not album.is_pub_date_valid()


class TestUserModel:
    def album_instance(self, title, artist):
        return Album(
            title=title,
            artist=artist,
            user_rating=random_user_rating(),
            genre=random_user_genre(),
            pub_date=present_date(),
            user=None,
            owned=None,
        )

    def get_albums_in_collection(self, domain_user):
        albums = Album.objects.filter(user=domain_user)
        albums_in_collection = filter(lambda album: album.owned == True, albums)
        return set(album for album in albums_in_collection)

    def get_albums_on_wishlist(self, domain_user):
        albums = Album.objects.filter(user=domain_user)
        albums_on_wishlist = filter(lambda album: album.owned == False, albums)
        return set(album for album in albums_on_wishlist)

    def test_new_user_has_an_empty_wishlist(self, domain_user):
        # When/Then
        assert len(self.get_albums_on_wishlist(domain_user)) == 0

    def test_new_user_has_an_empty_collection(self, domain_user):
        # When/Then
        assert len(self.get_albums_in_collection(domain_user)) == 0

    def test_add_to_collection_when_album_already_in_collection(self, albums_factory, domain_user):
        # Given
        albums_in_collection = albums_factory(owned=True)
        album_already_in_collection = choice(albums_in_collection)
        album_from_form = self.album_instance(
            album_already_in_collection.title, album_already_in_collection.artist
        )
        # When
        with pytest.raises(AlbumAlreadyInCollectionError):
            domain_user.add_to_collection(album_from_form)
        # Then
        assert len(self.get_albums_in_collection(domain_user)) == len(albums_in_collection)
        assert set(albums_in_collection) == set(self.get_albums_in_collection(domain_user))

    def test_add_to_collection_when_album_not_in_collection_and_not_on_wishlist(self, albums_factory, domain_user):
        # Given
        albums_in_collection = albums_factory(owned=True)
        albums_on_wishlist = albums_factory(owned=False)
        album_from_form = self.album_instance(random_string(), random_string())
        # When
        domain_user.add_to_collection(album_from_form)
        # Then
        assert len(self.get_albums_in_collection(domain_user)) == len(albums_in_collection) + 1
        assert len(self.get_albums_on_wishlist(domain_user)) == len(albums_on_wishlist)
        assert album_from_form in self.get_albums_in_collection(domain_user)

    def test_add_to_collection_when_album_on_wishlist(self, albums_factory, domain_user):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        album_on_wishlist = choice(albums_on_wishlist)
        album_from_form = self.album_instance(
            album_on_wishlist.title, album_on_wishlist.artist
        )
        # When
        domain_user.add_to_collection(album_from_form)
        # Then
        assert len(self.get_albums_in_collection(domain_user)) == 1
        assert album_from_form in self.get_albums_in_collection(domain_user)
        assert len(self.get_albums_on_wishlist(domain_user)) == len(albums_on_wishlist) - 1
        assert album_on_wishlist not in self.get_albums_on_wishlist(domain_user)

    def test_add_to_wishlist_when_album_not_on_wishlist(self, albums_factory, domain_user):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        album_from_form = self.album_instance(random_string(), random_string())
        # When
        domain_user.add_to_wishlist(album_from_form)
        # Then
        assert len(self.get_albums_on_wishlist(domain_user)) == len(albums_on_wishlist) + 1
        assert album_from_form in self.get_albums_on_wishlist(domain_user)

    def test_add_to_wishlist_when_album_already_on_wishlist(self, albums_factory, domain_user):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        album_on_wishlist = choice(albums_on_wishlist)
        album_from_form = self.album_instance(
            album_on_wishlist.title, album_on_wishlist.artist
        )
        # When/Then
        with pytest.raises(AlbumAlreadyOnWishlistError):
            domain_user.add_to_wishlist(album_from_form)
        assert len(self.get_albums_on_wishlist(domain_user)) == len(albums_on_wishlist)
        assert album_on_wishlist in self.get_albums_on_wishlist(domain_user)

    def test_add_to_wishlist_when_album_already_in_collection(self, albums_factory, domain_user):
        # Given
        albums_on_wishlist = albums_factory(owned=False)
        albums_in_collection = albums_factory(owned=True)
        album_in_collection = choice(albums_in_collection)
        album_from_form = self.album_instance(
            album_in_collection.title, album_in_collection.artist
        )
        # When/Then
        with pytest.raises(AlbumAlreadyInCollectionError):
            domain_user.add_to_wishlist(album_from_form)
        assert len(self.get_albums_on_wishlist(domain_user)) == len(albums_on_wishlist)
        assert album_from_form not in self.get_albums_on_wishlist(domain_user)

    @pytest.mark.parametrize("owned", [True, False])
    def test_edit_album_success(self, owned, albums_factory, domain_user):
        # Given
        albums = albums_factory(owned=owned)
        edited_album = choice(albums)
        album_from_form = self.album_instance(title=random_string(), artist=random_string())
        # When
        domain_user.edit_album(edited_album, album_from_form)
        # Then
        album_from_db = Album.objects.filter(title=album_from_form.title, artist=album_from_form.artist).first()
        assert album_from_db.pk == edited_album.pk
        assert album_from_db == album_from_form

    @pytest.mark.parametrize("owned", [True, False])
    def test_edit_album_duplicate_when_album_from_the_same_set(self, owned, albums_factory, domain_user):
        # Given
        albums = albums_factory(owned=owned)
        edited_album = choice(albums)
        other_album = choice(albums)
        while other_album == edited_album:
            other_album = choice(albums)
        album_from_form = self.album_instance(title=other_album.title, artist=other_album.artist)
        # When/Then
        with pytest.raises(AlbumAlreadyInCollectionError if owned else AlbumAlreadyOnWishlistError):
            domain_user.edit_album(edited_album, album_from_form)
        assert not edited_album == album_from_form

    @pytest.mark.parametrize("owned", [True, False])
    def test_edit_album_duplicate_when_album_from_different_set(self, owned, albums_factory, domain_user):
        # Given
        different_set = False if owned else True
        albums = albums_factory(owned=owned)
        albums_from_different_set = albums_factory(owned=different_set)
        edited_album = choice(albums)
        other_album = choice(albums_from_different_set)
        album_from_form = self.album_instance(title=other_album.title, artist=other_album.artist)
        # When/Then
        with pytest.raises(AlbumAlreadyInCollectionError if different_set else AlbumAlreadyOnWishlistError):
            domain_user.edit_album(edited_album, album_from_form)
        assert not edited_album == album_from_form
