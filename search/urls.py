from django.urls import path

from . import views

urlpatterns = [
    path("", views.search, name="search"),
    path("data_311", views.data_311, name="data_311"),
    path("data_res", views.data_res, name="data_res"),
]
