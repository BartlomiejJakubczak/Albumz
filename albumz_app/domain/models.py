from django.contrib.auth.models import User as AuthUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .. import constants
from .exceptions import (
    AlbumAlreadyInCollectionError,
    AlbumAlreadyOnWishlistError,
    AlbumDoesNotExistError,
)


class Genre(models.TextChoices):
    ROCK = "ROCK", "Rock"
    POP = "POP", "Pop"
    JAZZ = "JAZZ", "Jazz"
    HIPHOP = "HIPHOP", "Hip-Hop"
    OTHER = "OTHER", "Other"


class Rating(models.IntegerChoices):
    NO_OPINION_YET = 0
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

    @property
    def username(self):
        return self.auth_user.username

    def __str__(self) -> str:
        return f"{self.auth_user.username}"

    def add_to_collection(self, unsaved_album):
        existing_album = self.albums.filter(
            title=unsaved_album.title,
            artist=unsaved_album.artist,
        ).first()
        if existing_album:
            if existing_album.owned:
                raise AlbumAlreadyInCollectionError
            else:
                existing_album.owned = True
                existing_album.save()
        else:
            unsaved_album.user = self
            unsaved_album.owned = True
            unsaved_album.save()

    def add_to_wishlist(self, unsaved_album):
        existing_album = self.albums.filter(
            title=unsaved_album.title,
            artist=unsaved_album.artist,
        ).first()
        if existing_album:
            raise (
                AlbumAlreadyInCollectionError
                if existing_album.owned
                else AlbumAlreadyOnWishlistError
            )
        else:
            unsaved_album.user = self
            unsaved_album.owned = False
            unsaved_album.save()

    def edit_album(self, album_from_db, unsaved_album):
        existing_album = self.albums.filter(
            title=unsaved_album.title,
            artist=unsaved_album.artist,
        ).first()
        if existing_album and existing_album.pk != album_from_db.pk:
            raise (
                AlbumAlreadyInCollectionError
                if existing_album.owned
                else AlbumAlreadyOnWishlistError
            )
        else:
            fields_to_update = ["title", "artist", "pub_date", "genre", "user_rating"]
            for field in fields_to_update:
                setattr(album_from_db, field, getattr(unsaved_album, field))
            album_from_db.save()

    def move_to_collection(self, album_id):
        try:
            album = self.albums.get(pk=album_id)
        except Album.DoesNotExist:
            raise AlbumDoesNotExistError
        if album.owned:
            raise AlbumAlreadyInCollectionError
        album.owned = True
        album.save()


class AlbumQuerySet(models.QuerySet):
    def in_collection(self):
        return self.filter(owned=True)

    def for_user(self, user):
        return self.filter(user=user)

    def on_wishlist(self):
        return self.filter(owned=False)

    def average_rating(self, genre=None):
        if genre:
            return self.filter(genre=genre, user_rating__gt=0).aggregate(
                average_rating=models.Avg("user_rating")
            )
        return self.filter(user_rating__gt=0).aggregate(
            average_rating=models.Avg("user_rating")
        )

    def search_query(self, query):
        return self.filter(
            models.Q(artist__icontains=query) | models.Q(title__icontains=query)
        )


class AlbumManager(models.Manager):
    def get_queryset(self):
        return AlbumQuerySet(self.model, using=self._db)

    def average_rating(self, genre=None):
        return self.get_queryset().average_rating(genre)

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def in_collection(self):
        return self.get_queryset().in_collection()

    def on_wishlist(self):
        return self.get_queryset().on_wishlist()

    def search_query(self, query):
        if query:
            return self.get_queryset().search_query(query)
        return self.get_queryset()


class Album(models.Model):
    albums = AlbumManager()
    user = models.ForeignKey(User, models.CASCADE, related_name="albums")
    title = models.CharField(max_length=250)
    artist = models.CharField(max_length=100)
    pub_date = models.DateField("Date of publication.", null=True, blank=True)
    genre = models.CharField(max_length=30, choices=Genre.choices, default=Genre.OTHER)
    user_rating = models.IntegerField(
        "Rating given by the owner of the album.",
        choices=Rating.choices,
        null=False,
        blank=False,
        default=Rating.NO_OPINION_YET,
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
                {"pub_date": constants.ResponseStrings.PUB_DATE_ERROR}
            )

    def is_in_collection(self):
        return self.owned is True

    def is_on_wishlist(self):
        return self.owned is False

    def is_pub_date_valid(self):
        return self.pub_date is None or self.pub_date <= timezone.now().date()
