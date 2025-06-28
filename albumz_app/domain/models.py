from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone

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
    auth_user = models.OneToOneField(
        AuthUser, models.CASCADE, related_name="albumz_user"
    )

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
                album_in_question.user_rating = album.user_rating
                album_in_question.save()

    def add_to_wishlist(self, album):
        if album not in self.albums.all():
            album.user = self
            album.owned = False
            album.save()
        else:
            album_in_question = self.albums.get(title=album.title, artist=album.artist)
            raise (
                AlbumAlreadyOwnedError
                if album_in_question.owned
                else AlbumAlreadyOnWishlistError
            )


class Album(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name="albums")
    title = models.CharField(max_length=250)
    artist = models.CharField(max_length=100)
    pub_date = models.DateField("Date of publication.", null=True, blank=True)
    genre = models.CharField(max_length=30, choices=Genre.choices, default=Genre.OTHER)
    user_rating = models.IntegerField(
        "Rating given by the owner of the album.", choices=Rating.choices, null=True, blank=False, default=None
    )
    add_date = models.DateField("Date of adding to the system.", auto_now_add=True)
    owned = models.BooleanField(
        "True if owned, False if on wishlist"
    )  # None as default

    def __str__(self):
        return f"{self.title} by {self.artist}"

    def __eq__(self, value) -> bool:  # default behaviour is comparison by primary keys
        if not isinstance(value, Album):
            return False
        return self.title == value.title and self.artist == value.artist

    def __hash__(self):
        return hash((self.title, self.artist))

    def clean(self):
        super().clean()
        if not self.is_pub_date_valid():
            raise ValidationError(
                {"pub_date": "Publication date cannot be in the future."}
            )

    def is_in_collection(self):
        return self.owned == True

    def is_on_wishlist(self):
        return self.owned == False

    def is_pub_date_valid(self):
        return self.pub_date is None or self.pub_date <= timezone.now().date()
