from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
    path("", views.api_root),
    path("albums/", views.AlbumsList.as_view(), name="api_album_list"),
    path("albums/<int:pk>/", views.AlbumDetail.as_view(), name="api_album_detail"),
    path("users/", views.UsersList.as_view(), name="api_user_list"),
    path("users/<int:pk>/", views.UserDetail.as_view(), name="api_user_detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)