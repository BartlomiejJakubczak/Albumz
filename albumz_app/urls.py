from django.urls import path

from . import views

app_name="albumz"
urlpatterns = [
    # ex: /albumz/
    path("", views.IndexView.as_view(), name="index"),
    # ex: /albumz/album/5/
    path("album/<int:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /albumz/album/5/rate/
    path("album/<int:album_id>/rate/", views.rate, name="rate"),
    # ex: /albumz/artist/1/results/
    path("artist/<int:pk>/results/", views.ResultsView.as_view(), name="results"),
]