from django.contrib import admin
from .models import Location, Apartment, ClaimRequest

admin.site.register(Location)
admin.site.register(Apartment)
admin.site.register(ClaimRequest)
