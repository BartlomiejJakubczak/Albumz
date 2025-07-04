from django.utils import timezone
from datetime import timedelta
from random import randint, choice
from string import ascii_letters, digits

from ..domain.models import Rating


def random_string():
            return "".join(choice(ascii_letters) for _ in range(randint(1, 10)))

def random_user_rating():
    return choice(Rating.choices)[0]

def future_date():
    return timezone.now().date() + timedelta(days=1)

def present_date():
    return timezone.now().date()

def random_positive_number(length=None):
    if length is None:
        length = randint(1, 10)
    return int("".join((choice(digits) for _ in range(length))))
