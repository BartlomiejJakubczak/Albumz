from random import randint, choice
from string import ascii_letters

from .utils import get_random_user_rating
from ..domain.models import Album

class AlbumFactoryMixin:
    def create_albums(self, owned, count=randint(1, 10), user=None):
        def create_random_string():
            return "".join(choice(ascii_letters) for _ in range(randint(1, 10)))
        
        albums_in_collection = []
        if user is None:
            if not hasattr(self, "domain_user"):
                raise AttributeError("Test class must define self.domain_user")
            user = self.domain_user
        for _ in range(count):
            albums_in_collection.append(
                Album.objects.create(
                    title=create_random_string(),
                    artist=create_random_string(),
                    user=user,
                    owned=owned,
                    user_rating = get_random_user_rating() if owned else None,
                )
            )
        return albums_in_collection