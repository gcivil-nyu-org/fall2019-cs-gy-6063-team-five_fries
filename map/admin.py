from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import CityStreetSpot

admin.site.register(CityStreetSpot)
# Register your models here.
