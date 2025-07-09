from django.urls import path

from . import views

app_name = "albumz"
urlpatterns = [
    # ex: /albumz/album/5/
    path("album/<int:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /albumz/album/5/delete
    path("album/<int:pk>/delete/", views.AlbumDeleteView.as_view(), name="delete"),
    # ex: /albumz/album/5/edit
    path("album/<int:pk>/edit/", views.EditView.as_view(), name="edit"),
    # ex: /albumz/album/5/move
    path("album/<int:pk>/move/", views.move_to_collection_view, name="move"),
    # ex: /albumz/collection/
    path("collection/", views.CollectionView.as_view(), name="collection"),
    # ex: /albumz/collection/add
    path("collection/add/", views.AlbumAddColletionView.as_view(), name="add_collection"),
    # ex: /albumz/wishlist/
    path("wishlist/", views.WishlistView.as_view(), name="wishlist"),
    # ex: /albumz/wishlist/add
    path("wishlist/add/", views.AlbumAddWishlistView.as_view(), name="add_wishlist"),
]
