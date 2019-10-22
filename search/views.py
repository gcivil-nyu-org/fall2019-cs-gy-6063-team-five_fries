from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.utils import timezone
from craigslist import CraigslistHousing
from .GetRentalHouse import get_rental_house
from .forms import ZillowSearchForm
from .models import CraigslistLocation, LastRetrievedData
import json
import requests

from data_311.get_311_data import get_311_data


class CraigslistIndexView(generic.ListView):
    template_name = "search/clist_results.html"
    context_object_name = "cl_results"


def search(request):
    if request.method == "POST" and "zillow" in request.POST:
        form = ZillowSearchForm(request.POST)
        if form.is_valid():
            address = request.POST["address"]
            city_state_zip = request.POST["city_state_zip"]
            rent_z_estimate = "true"

            json_data = json.loads(
                get_rental_house(address, city_state_zip, rent_z_estimate)
            )
            results = json_data["SearchResults:searchresults"]["response"]["results"][
                "result"
            ]
            return render(request, "search/result.html", {"z_results": results})
    else:
        # render an error
        form = ZillowSearchForm()
        return render(request, "search/search.html", {"form": form})


# TODO: Display data beautifully
def result(request):
    return HttpResponse("Result Page")


def error(request):
    return HttpResponse("This is index of Error")


def data_311(request):
    if request.method == "POST":
        zip_code = request.POST["zip_code"]
        query_results, timeout, no_matches = get_311_data(str(zip_code))

        return render(
            request,
            "search/results_311.html",
            {"results": query_results, "timeout": timeout, "no_matches": no_matches},
        )

    else:
        return render(request, "search/data_311.html", {})


def clist_results(request):
    do_update = False
    last, created = LastRetrievedData.objects.get_or_create(model="CraigslistLocation")

    if created:
        do_update = True
    elif last.should_retrieve():
        do_update = True
        last.time = timezone.now()
        last.save()

    results = []
    if do_update is True:
        cl_h = CraigslistHousing(
            site="newyork", category="apa", area="brk", filters={"max_price": 2000}
        )
        results = cl_h.get_results(geotagged=True)

    for r in results:
        if not CraigslistLocation.objects.filter(c_id=r["id"]).exists():
            lat = None
            lon = None
            if r["geotag"] is not None:
                lat = r["geotag"][0]
                lon = r["geotag"][1]

            q = CraigslistLocation(
                c_id=r["id"],
                name=r["name"],
                url=r["url"],
                date_time=r["datetime"],
                price=r["price"],
                where=(r["where"] if r["where"] is not None else ""),
                has_image=r["has_image"],
                lat=lat,
                lon=lon,
            )
            q.save()
    result_list = CraigslistLocation.objects.all()
    context = {"clist_results": result_list}
    return render(request, "search/clist_results.html", context)



def restraunts(request):
    data_restraunts= requests.get("https://data.cityofnewyork.us/resource/43nn-pn8j.json?grade=A")
    def jprint(obj):
        # create a formatted string of the Python JSON object
        text = json.dumps(obj, sort_keys=True, indent=4)
        print(text)

    jprint(data_restraunts.json())
    data_restraunts = data_restraunts.text
    return render(request, "search/data_restraunts.html", {})

