from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "accounts"
urlpatterns = [
    # ex: /accounts/register
    path("register/", views.RegisterView.as_view(), name="register"),
    # ex: /accounts/login
    path("login/", views.LoginView.as_view(), name="login"),
    # ex: /accounts/logout
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
