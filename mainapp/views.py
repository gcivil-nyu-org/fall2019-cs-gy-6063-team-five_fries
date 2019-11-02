from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse
from secret import get_google_api_key

from pygeocoder import Geocoder
import googlemaps

import json


class LoginView(TemplateView):
    template_name = "login.html"

    def post(self, request, *args, **kwargs):
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))

        else:
            return HttpResponseRedirect(reverse("login"))


def index(request):
    return render(request, "index.html")


@login_required
def account(request):
    return render(request, "account.html", {"user": request.user})


def search(request):
    return HttpResponseRedirect(reverse("search"))


def geo(request):
    req = request.POST.get("geotext")

    # gmaps = googlemaps.Client(key=get_google_api_key())
    coder = Geocoder(api_key=get_google_api_key())
    result = coder.geocode(str(req))
    # pyresult = dict(result)
    # result = gmaps.geocode(str(req))

    pretty = json.dumps(result.__dict__, sort_keys=True, indent=4)

    return HttpResponse(
        f"Your search was {req} and response was {result} and pretty: {pretty}"
    )
