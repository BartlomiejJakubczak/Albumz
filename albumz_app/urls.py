from django.urls import path

from . import views

app_name="albumz"
urlpatterns = [
    # ex: /albumz/
    path("", views.index, name="index"),
    # ex: /albumz/album/5/
    path("album/<int:album_id>/", views.detail, name="detail"),
    # ex: /albumz/album/5/vote/
    path("album/<int:album_id>/vote/", views.rate, name="rate"),
    # ex: /albumz/artist/1/results/
    path("artist/<int:artist_id>/results/", views.results, name="results"),
]