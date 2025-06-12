from django.urls import path

from . import views

app_name="albumz"
urlpatterns = [
    # ex: /albumz/album/5/
    path("album/<int:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /albumz/results/
    path("results/", views.ResultsView.as_view(), name="results"),
]