from django.shortcuts import render
from django.views import generic
from django.utils import timezone
from .models import CraigslistLocation, LastRetrievedData
from location.models import Location


from external.nyc311 import get_311_data, get_311_statistics
from external.craigslist import fetch_craigslist_housing


class CraigslistIndexView(generic.ListView):
    template_name = "search/clist_results.html"
    context_object_name = "cl_results"


def search(request):
    # generic zip code form post
    if request.method == "GET":
        timeout = False
        zip_code = request.GET.get("zipcode")
        search_data = {}
        if zip_code:
            search_data["locations"] = Location.objects.filter(zipcode=str(zip_code))

            # Get 311 statistics
            try:
                stats = get_311_statistics(str(zip_code))
                search_data["stats"] = [
                    (s.complaint_type, 100 * s.complaint_level / 5) for s in stats
                ]
            except TimeoutError:
                timeout = True

        return render(
            request,
            "search/search.html",
            {"search_data": search_data, "zip": str(zip_code), "timeout": timeout},
        )
    else:
        # render an error
        return render(request, "search/search.html")


def data_311(request):
    if request.method == "GET" and "zip_code" in request.GET:
        zip_code = request.GET["zip_code"]

        results = {}
        timeout = False
        # Get 311 statistics
        try:
            results["stats"] = get_311_statistics(str(zip_code))
        except TimeoutError:
            timeout = True

        # Get 311 raw complaints
        try:
            results["complaints"] = get_311_data(str(zip_code))
        except TimeoutError:
            timeout = True

        return render(
            request,
            "search/results_311.html",
            {
                "results": results,
                "zip_code": str(zip_code),
                "no_matches": len(results) == 0,
                "timeout": timeout,
            },
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
