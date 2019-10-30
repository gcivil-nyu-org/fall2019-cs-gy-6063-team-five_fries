from django.shortcuts import render
from django.views import generic
from django.utils import timezone
from .GetRentalHouse import get_rental_house
from .forms import ZillowSearchForm
from .models import CraigslistLocation, LastRetrievedData
import json


from external.nyc311 import get_311_data, get_311_statistics
from external.craigslist import fetch_craigslist_housing


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
    # generic zip code form post
    elif request.method == "GET":
        zip_code = request.GET.get("zipcode")
        search_data = {}
        if zip_code:
            search_data["locations"] = fetch_craigslist_housing(
                limit=25,  # FIXME: temporarily limit the results up to 25 for the fast response
                site="newyork",
                category="apa",
                filters={"zip_code": str(zip_code)},
            )
        # TODO add 311 statistics
        """
        try:
            search_data['stats'] = get_311_statistics(str(zip_code))
        except TimeoutError:
            return render(request, "search/statistics_311.htm", {"timeout": True})
        """
        return render(
            request,
            "search/search.html",
            {"search_data": search_data, "zip": str(zip_code)},
        )
    else:
        # render an error
        form = ZillowSearchForm()
        return render(request, "search/search.html", {"form": form})


def data_311(request):
    if request.method == "POST" and "data" in request.POST:
        zip_code = request.POST["zip_code"]
        try:
            results = get_311_data(str(zip_code))
        except TimeoutError:
            return render(request, "search/results_311.html", {"timeout": True})

        return render(
            request,
            "search/results_311.html",
            {"results": results, "no_matches": len(results) == 0},
        )

    elif request.method == "POST" and "statistics" in request.POST:
        zip_code = request.POST["zip_code"]
        try:
            results = get_311_statistics(str(zip_code))
        except TimeoutError:
            return render(request, "search/statistics_311.htm", {"timeout": True})

        return render(
            request,
            "search/statistics_311.html",
            {"zip": zip_code, "results": results, "no_matches": len(results) == 0},
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
        results = fetch_craigslist_housing(
            limit=100,  # FIXME: temporarily limit the results up to 100 for the fast response
            site="newyork",
            category="apa",
            area="brk",
            filters={"max_price": 2000},
        )

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
