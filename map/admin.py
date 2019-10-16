from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import CityStreetSpot

admin.site.register(CityStreetSpot)
#admin.site.register(CityStreetSpot, LeafletGeoAdmin) enable-drag-drop marker in admin page
