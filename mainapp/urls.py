from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/", include("allauth.urls")),
    # path("login", views.LoginView.as_view(), name="login"),
    # path("account", views.account, name="account"),
]
