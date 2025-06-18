from django.contrib import admin

from .domain.models import Album, User

class AlbumInline(admin.TabularInline):
    model = Album
    extra = 3

class UserAdmin(admin.ModelAdmin):
    inlines = [AlbumInline]

class AlbumAdmin(admin.ModelAdmin):
    list_display = ["title", "artist", "add_date", "user"]
    list_filter = ["add_date"]
    search_fields = ["title", "artist"]

admin.site.register(User, UserAdmin)
admin.site.register(Album, AlbumAdmin)