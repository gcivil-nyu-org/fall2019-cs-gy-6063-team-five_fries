from django.urls import path

from . import views

urlpatterns = [
    path("", views.sim_apt, name="similar_apartments"),
]
