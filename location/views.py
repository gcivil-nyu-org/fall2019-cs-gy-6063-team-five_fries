from django.views import generic
from .models import Location
from external.cache.zillow import refresh_zillow_housing_if_needed
from mainapp.models import SiteUser
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


class LocationView(generic.DetailView):
    model = Location
    template_name = "location.html"

    def get_object(self):
        obj = super().get_object()
        refresh_zillow_housing_if_needed(obj)
        return obj
def favorites(request, pk):

    apartment = get_object_or_404(Location, pk = pk)
    print("print")
    # user = get_object_or_404(SiteUser, pk= user)
    # user.favorites.add(apartment)
    # favorited_apartments = user.favorites.all()
    # print("Apartment selected as favorite!!!")
    # return render(request, reverse("location", args=(1,), {"favorited_apartments": favorited_apartments}))
    # return render(request, reverse("location", args=pk), {})
    # return render(reverse("location", args=(pk,)), {})
    return render(request, reverse("location", args=(pk,)), {})
