from django.contrib import admin

from .domain.models import Artist, Album
# Register your models here.

admin.site.register(Artist)
admin.site.register(Album)