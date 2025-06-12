from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name="accounts"
urlpatterns = [
    # ex: /accounts/register
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
]