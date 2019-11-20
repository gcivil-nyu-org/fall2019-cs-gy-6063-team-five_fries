from django.urls import path

from . import views

urlpatterns = [
    path("<int:pk>/", views.LocationView.as_view(), name="location"),
    path(
        "<int:pk>/apartment/<suite_num>", views.apartment_detail_view, name="apartment"
    ),
    path("<int:pk>/apartment/<suite_num>/claim", views.claim_view, name="claim"),
    path(
        "<int:pk>/apartment/<suite_num>/contact_landlord",
        views.contact_landlord,
        name="contact_landlord",
    ),
    path(
        "<int:pk>/apartment/<suite_num>/edit",
        views.apartment_edit,
        name="apartment_edit",
    ),
    path("<int:pk>/favorite", views.favorites, name="favorite"),
    path("favlist", views.favlist, name="favlist"),
    path("<int:pk>/review", views.review, name="review"),
    path("apartment_upload", views.apartment_upload, name="apartment_upload"),
    path(
        "apartment_upload_confirmation",
        views.apartment_upload_confirmation,
        name="apartment_upload_confirmation",
    ),
]
