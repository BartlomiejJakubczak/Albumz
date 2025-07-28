from django.urls import include, path
from rest_framework.routers import DefaultRouter

from albumz_app.constants import API_APP_NAME

from . import views

router = DefaultRouter()
router.register(r"albums", views.AlbumsViewSet, basename="album")

app_name = API_APP_NAME
urlpatterns = [
    path("", include(router.urls)),
]

# urlpatterns = format_suffix_patterns(urlpatterns) ONLY TO BE USED WITHOUT DRF ROUTING
