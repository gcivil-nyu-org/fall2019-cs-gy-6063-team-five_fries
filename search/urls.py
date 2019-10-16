from django.urls import path

from . import views

urlpatterns = [
    path("", views.search, name="search"),
    path("result", views.result, name="result"),
    path("error", views.result, name="error"),
    path("data_311", views.data_311, name="data_311"),
    path("clist_results", views.clist_results, name="clist_results"),
]
