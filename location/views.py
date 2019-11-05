from django.views import generic
from .models import Location
from external.cache.zillow import refresh_zillow_housing_if_needed
from mainapp.models import SiteUser
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render


class LocationView(generic.DetailView):
    model = Location
    template_name = "location.html"

    def get_object(self):
        obj = super().get_object()
        refresh_zillow_housing_if_needed(obj)
        return obj

@login_required
def favorites(request, pk):
    apartment = get_object_or_404(Location, pk=pk)
    user = request.user
    user.favorites.add(apartment)
    messages.success(request, "This apartment has been added to your favorites!")
    return HttpResponseRedirect(reverse("location", args=(pk,)))


@login_required
def favlist(request):
    favorited_apartments = request.user.favorites.all()
    return render(
        request, "favlist.html", {"favorited_apartments": favorited_apartments}
    )
