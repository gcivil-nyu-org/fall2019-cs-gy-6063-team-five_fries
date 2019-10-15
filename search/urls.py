from django.urls import path

from . import views

urlpatterns = [
    path("", views.search, name="search"),
    path("result", views.result, name="result"),
    path("error", views.result, name="error"),
    # path("cl_results", views.CraigslistIndexView.as_view(), name="clist_results")
    path("clist_results", views.clist_results, name="clist_results"),
]
