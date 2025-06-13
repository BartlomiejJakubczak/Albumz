from django.db import models
from django.contrib.auth.models import User as AuthUser

from .exceptions import (
    AlbumAlreadyOnWishlistError,
    AlbumAlreadyOwnedError,
    AlbumDoesNotExistError,
)

class Genre(models.TextChoices):
    ROCK = "ROCK", "Rock"
    POP = "POP", "Pop"
    JAZZ = "JAZZ", "Jazz"
    HIPHOP = "HIPHOP", "Hip-Hop"
    OTHER = "OTHER", "Other"

class Rating(models.IntegerChoices):
    TERRIBLE = 1
    BAD = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5
    BEST = 6

class User(models.Model):
    auth_user = models.OneToOneField(AuthUser, models.CASCADE, related_name="albumz_user")
    
    def __str__(self) -> str:
        return f"{self.auth_user.username}"

    def add_to_collection(self, album):
        if album not in self.albums.all():
            album.user = self
            album.owned = True
            album.save()
        else:
            album_in_question = self.albums.get(title=album.title, artist=album.artist)
            if album_in_question.is_in_collection():
                raise AlbumAlreadyOwnedError
            else:
                album_in_question.owned = True
                album_in_question.save()
        
    def remove_from_collection(self, pk):
        try:
            album = self.albums.get(pk=pk)
            album.delete()
        except Album.DoesNotExist:
            raise AlbumDoesNotExistError

    def get_collection(self):
        albums = self.albums.all()
        return set(album for album in filter(lambda album: album.owned == True, albums))
        
    def add_to_wishlist(self, album):
        if album not in self.albums.all():
            album.user = self
            album.owned = False
            album.save()
        else:
            album_in_question = self.albums.get(title=album.title, artist=album.artist)
            raise AlbumAlreadyOwnedError if album_in_question.owned else AlbumAlreadyOnWishlistError
    
    def remove_from_wishlist(self, pk):
        try:
            album = self.albums.get(pk=pk)
            album.delete()
        except Album.DoesNotExist:
            raise AlbumDoesNotExistError

class Album(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name="albums") # excluded from form data
    title = models.CharField(max_length=250)
    artist = models.CharField(max_length=100)
    pub_date = models.DateField("Date of publication.", null=True, blank=True)
    genre = models.CharField(
        max_length=30,
        choices=Genre.choices,
        default=Genre.OTHER
    )
    user_rating = models.IntegerField(
        "Rating given by the owner of the album.", 
        choices=Rating.choices, 
        default=0
    )
    add_date = models.DateField("Date of adding to the system.", auto_now_add=True)
    owned = models.BooleanField("True if owned, False if on wishlist") # None as default

    def __str__(self):
        return f"{self.title} by {self.artist}"
    
    def __eq__(self, value) -> bool: # default behaviour is comparison by primary keys
        if not isinstance(value, Album):
            return False
        return self.title == value.title and self.artist == value.artist
    
    def __hash__(self):
        return hash(self.title + self.artist)
    
    def is_in_collection(self):
        return self.owned == True
    
    def is_on_wishlist(self):
        return self.owned == False
