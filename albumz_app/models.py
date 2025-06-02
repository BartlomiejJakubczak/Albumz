import datetime

from django.db import models
from django.utils import timezone

# Create your models here.

class Genre(models.TextChoices):
    ROCK = "ROCK", "Rock"
    POP = "POP", "Pop"
    JAZZ = "JAZZ", "Jazz"
    HIPHOP = "HIPHOP", "Hip-Hop"
    OTHER = "OTHER", "Other"

class Artist(models.Model):
    name = models.CharField(max_length=250)
    country = models.CharField(max_length=100, blank=True) # blank = may be empty in form
    formed_year = models.PositiveIntegerField(null=True, blank=True) # null = may be empty in database

    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=250)
    artist = models.ForeignKey(Artist, models.CASCADE, related_name="albums") # many-to-one, related_name names relation from the related 
    # object back to this one, a reverse relationship, so artist.albums.all() works

    # example Django's ORM call:

    # Album.objects.filter(artist__country="Poland") 
    # which translates to:
    # SELECT * FROM album WHERE artist.country = 'Poland';

    # Django automatically handles the join between Album and Artist for you.

    # The full SQL query would look like this:
    # SELECT album.* FROM album JOIN artist ON album.artist_id = artist.id
    # WHERE artist.country = 'Poland';
    pub_date = models.DateField("Date of publication.")
    genre = models.CharField(
        max_length=30,
        choices=Genre.choices,
        default=Genre.OTHER
    )

    def __str__(self):
        return f"{self.title} by {self.artist.name}"
    
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(weeks=4) # this is possible due to __ge__ (greater-equal) and __sub__ of datetime

