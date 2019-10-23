from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/",views.search, name="search"),
    path("login", views.LoginView.as_view(), name="login"),
    path("account", views.account, name="account"),
]
