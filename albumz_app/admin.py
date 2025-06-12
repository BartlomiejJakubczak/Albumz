from django.contrib import admin

from .domain.models import Album, User

admin.site.register(Album)
admin.site.register(User)