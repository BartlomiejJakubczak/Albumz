import datetime

from django.db import models
from django.utils import timezone
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
    # auth_user = models.OneToOneField(AuthUser, models.CASCADE, null=True)
    
    def add_to_collection(self, album):
        if album not in self.albums.all():
            album.user = self
            album.owned = True
            album.save()
        else:
            album_in_question = self.albums.get(title=album.title, artist=album.artist)
            if album_in_question.is_owned():
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

class Artist(models.Model):
    name = models.CharField(max_length=250)
    country = models.CharField(max_length=100, null=True, blank=True)
    formed_year = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=250)
    artist = models.ForeignKey(Artist, models.CASCADE, related_name="albums") # many-to-one, related_name names relation from the related 
    # object back to this one, a reverse relationship, so artist.albums.all() works

    # example Django's ORM call:

    # Album.objects.filter(artist__country="Poland") (note: there's a hidden __exact field lookup here, so artist__country__exact would be the full explicit call)
    # which translates to:
    # SELECT * FROM album WHERE artist.country = 'Poland';

    # Django automatically handles the join between Album and Artist for you.

    # The full SQL query would look like this:
    # SELECT album.* FROM album JOIN artist ON album.artist_id = artist.id
    # WHERE artist.country = 'Poland';
    user = models.ForeignKey(User, models.CASCADE, related_name="albums") # excluded from form data
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
        return f"{self.title} by {self.artist.name}"
    
    def __eq__(self, value) -> bool: # default behaviour is comparison by primary keys
        return self.title == value.title and self.artist.name == value.artist.name
    
    def __hash__(self):
        return hash(self.pk)
    
    def is_owned(self):
        return self.owned == True
    
    def is_on_wishlist(self):
        return self.owned == False
