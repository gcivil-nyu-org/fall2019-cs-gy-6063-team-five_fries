from django.views import generic
from .models import Location


class LocationView(generic.DetailView):
    model = Location
    template_name = "location.html"
