from django.urls import path

from . import views

urlpatterns = [
    path("autofetch", views.autofetch, name="autofetch"),
]