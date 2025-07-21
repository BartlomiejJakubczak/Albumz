from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r"albums", views.AlbumsViewSet, basename="album")


urlpatterns = [
    path("", include(router.urls)),
]

# urlpatterns = format_suffix_patterns(urlpatterns) ONLY TO BE USED WITHOUT DRF ROUTING