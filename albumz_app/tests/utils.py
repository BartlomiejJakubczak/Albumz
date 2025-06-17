from string import ascii_letters
from random import choice, randint

from ..domain.models import Album

class AlbumTestHelpers:
    def create_albums(self, owned, count=randint(1, 10), user=None):
        def create_random_string():
            return str((''.join(choice(ascii_letters)) for _ in range(randint(1, 10))))
        
        if user is None:
            if not hasattr(self, "domain_user"):
                raise AttributeError("Test class must define self.domain_user")
            user = self.domain_user
        albums_in_collection = []
        for _ in range(count):
            albums_in_collection.append(
                Album.objects.create(
                    title=create_random_string(), 
                    artist=create_random_string(), 
                    user=user,
                    owned=owned,
                )
            )
        return albums_in_collection