from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.utils import timezone

from craigslist import CraigslistHousing

from .GetRentalHouse import getRentalHouse
from .forms import ZillowSearchForm
from .models import CraigslistLocation, LastRetrievedData
import json
from data_311.get_311_data import get_311_data


class CraigslistIndexView(generic.ListView):
    template_name = "search/clist_results.html"
    context_object_name = "cl_results"


def search(request):
    if request.method == "POST" and "zillow" in request.POST:
        form = ZillowSearchForm(request.POST)
        if form.is_valid():
            address = request.POST["address"]
            cityStateZip = request.POST["cityStateZip"]
            rentZestimate = "true"

            jsonData = json.loads(getRentalHouse(address, cityStateZip, rentZestimate))
            results = jsonData["SearchResults:searchresults"]["response"]["results"][
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
    doUpdate = False
    last, created = LastRetrievedData.objects.get_or_create(model="CraigslistLocation")

    if created:
        doUpdate = True
    elif last.should_retrieve():
        doUpdate = True
        last.time = timezone.now()
        last.save()

    results = []
    if doUpdate is True:
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
