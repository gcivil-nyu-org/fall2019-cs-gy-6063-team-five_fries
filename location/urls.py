from django.urls import path

from . import views

urlpatterns = [
    path("<int:pk>/", views.LocationView.as_view(), name="location"),
    path("<int:pk>/apartment/<int:apk>", views.apartment_detail_view, name="apartment"),
    path(
        "<int:pk>/apartment/<int:apk>/complaints",
        views.apartment_complaints,
        name="complaints",
    ),
    path("<int:pk>/apartment/<int:apk>/claim", views.claim_view, name="claim"),
    path(
        "<int:pk>/apartment/<int:apk>/grant/<int:id>/<uuid:token>",
        views.grant_claim,
        name="grant_claim",
    ),
    path(
        "<int:pk>/apartment/<int:apk>/deny/<int:id>/<uuid:token>",
        views.deny_claim,
        name="deny_claim",
    ),
    path(
        "<int:pk>/apartment/<int:apk>/contact_landlord",
        views.contact_landlord,
        name="contact_landlord",
    ),
    path(
        "<int:pk>/apartment/<int:apk>/edit", views.apartment_edit, name="apartment_edit"
    ),
    path(
        "<int:pk>/apartment/<int:apk>/delete",
        views.apartment_delete,
        name="apartment_delete",
    ),
    path("<int:pk>/favorite", views.favorites, name="favorite"),
    path("favlist", views.favlist, name="favlist"),
    path("<int:pk>/review", views.review, name="review"),
    path("apartment_upload", views.apartment_upload, name="apartment_upload"),
]
