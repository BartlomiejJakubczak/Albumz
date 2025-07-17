from django.urls import path

from albumz_app import views, constants


app_name = constants.APP_NAME
urlpatterns = [
    # ex: /albumz/album/5/
    path("album/<int:pk>/", views.DetailView.as_view(), name=constants.URLNames.DETAIL),
    # ex: /albumz/album/5/delete
    path("album/<int:pk>/delete/", views.AlbumDeleteView.as_view(), name=constants.URLNames.DELETE),
    # ex: /albumz/album/5/edit
    path("album/<int:pk>/edit/", views.EditView.as_view(), name=constants.URLNames.EDIT),
    # ex: /albumz/album/5/move
    path("album/<int:pk>/move/", views.move_to_collection_view, name=constants.URLNames.MOVE_TO_COLLECTION),
    # ex: /albumz/collection/
    path("collection/", views.CollectionView.as_view(), name=constants.URLNames.COLLECTION),
    # ex: /albumz/collection/add
    path("collection/add/", views.AlbumAddColletionView.as_view(), name=constants.URLNames.ADD_TO_COLLECTION),
    # ex: /albumz/wishlist/
    path("wishlist/", views.WishlistView.as_view(), name=constants.URLNames.WISHLIST),
    # ex: /albumz/wishlist/add
    path("wishlist/add/", views.AlbumAddWishlistView.as_view(), name=constants.URLNames.ADD_TO_WISHLIST),
]
