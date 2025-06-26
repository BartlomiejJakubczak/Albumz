from django.urls import path

from . import views

app_name = "albumz"
urlpatterns = [
    # ex: /albumz/album/5/
    path("album/<int:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /albumz/collection/
    path("collection/", views.ResultsView.as_view(), name="collection"),
    # ex: /albumz/collection/create
    path("collection/add/", views.add_album_collection, name="add_collection"),
    # ex: /albumz/wishlist/
    path("wishlist/", views.WishlistView.as_view(), name="wishlist"),
]
