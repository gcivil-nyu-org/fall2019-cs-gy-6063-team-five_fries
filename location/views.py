from django.views import generic
from .models import Location
from external.cache.zillow import refresh_zillow_housing_if_needed


class LocationView(generic.DetailView):
    model = Location
    template_name = "location.html"

    def get_object(self):
        obj = super().get_object()
        refresh_zillow_housing_if_needed(obj)
        return obj
