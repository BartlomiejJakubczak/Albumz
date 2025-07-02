from random import randint
from .utils import random_user_rating, random_string
from ..domain.models import Album

class AlbumFactoryMixin:
    def create_albums(self, owned, count=randint(1, 10), user=None):
        albums_in_collection = []
        if user is None:
            if not hasattr(self, "domain_user"):
                raise AttributeError("Test class must define self.domain_user")
            user = self.domain_user
        for _ in range(count):
            albums_in_collection.append(
                Album.objects.create(
                    title=random_string(),
                    artist=random_string(),
                    user=user,
                    owned=owned,
                    user_rating = random_user_rating() if owned else None,
                )
            )
        return albums_in_collection