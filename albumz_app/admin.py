from django.contrib import admin

from .domain.models import Artist, Album, User

admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(User)