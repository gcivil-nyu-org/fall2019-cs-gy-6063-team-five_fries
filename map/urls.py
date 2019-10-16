from django.urls import path
from django.conf.urls import url
from djgeojson.views import GeoJSONLayerView
from . import views
from .models import CityStreetSpot

urlpatterns = [
    path("", views.mapview, name="mapview"),
    path("search", views.search, name="search"),
    url(r'^data.geojson$', GeoJSONLayerView.as_view(model=CityStreetSpot, properties=('title', 'description', 'picture_url')), name='data')
]
