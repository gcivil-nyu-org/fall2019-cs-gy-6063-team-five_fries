from django.shortcuts import render
from django.views import generic
from django.utils import timezone
from .models import CraigslistLocation, LastRetrievedData
from .forms import SearchForm
from location.models import Location

from external.nyc311 import get_311_data, get_311_statistics
from external.craigslist import fetch_craigslist_housing


class CraigslistIndexView(generic.ListView):
    template_name = "search/clist_results.html"
    context_object_name = "cl_results"


def search(request):
    # generic zip code form post
    if request.method == "GET":

        # pass the form data to the form class
        search_form = SearchForm(request.GET)

        timeout = False
        zip_code = request.GET.get("zipcode")
        max_price = request.GET.get("max_price")
        min_price = request.GET.get("min_price")
        bed_num = request.GET.get("bed_num")

        search_title = ""

        # build the query parameter dictionary that will be used to
        # query the Location model
        query_params = build_search_query(
            zip_code=zip_code, max_price=max_price, min_price=min_price, bed_num=bed_num
        )

        search_data = {}
        if query_params.keys() and search_form.is_valid():

            if zip_code:
                search_title = search_title + f"Zipcode: {zip_code} "
            if min_price:
                search_title = search_title + f"Min Price: {min_price} "
            if max_price:
                search_title = search_title + f"Max Price: {max_price} "
            if bed_num:
                search_title = search_title + f"Number of Bedroom: {bed_num}"

            search_data["locations"] = Location.objects.filter(**query_params)
            # Get 311 statistics
            try:
                stats = get_311_statistics(str(zip_code))
                search_data["stats"] = [
                    (s.complaint_type, 100 * s.complaint_level / 5) for s in stats
                ]
                average_complaint_level = sum(s.complaint_level for s in stats) / len(
                    stats
                )
                search_data["average_complaint_level"] = average_complaint_level
                search_data[
                    "description_for_complaint_level"
                ] = description_for_complaint_level(average_complaint_level)
                search_data[
                    "css_color_for_complaint_level"
                ] = css_color_for_complaint_level(average_complaint_level)
            except TimeoutError:
                timeout = True

        return render(
            request,
            "search/search.html",
            {
                "search_data": search_data,
                "zip": zip_code,
                "search_title": search_title,
                "search_form": search_form,
                "timeout": timeout,
            },
        )
    else:
        # render an error
        search_form = SearchForm()
        return render(request, "search/search.html", {"search_form": search_form})


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


def description_for_complaint_level(level):
    """
    Return an emoji for given complaint_level in the range [0, 5]
    """
    level = round(min(max(0, level), 5))
    return [
        "Very low 😊",
        "Low 🙂",
        "Neutral low 😐",
        "Neutral high 🤔",
        "High 😞",
        "Very high 😡",
    ][level]


def css_color_for_complaint_level(level):
    level = round(min(max(0, level), 5))
    colors = ["lightgreen", "lightgreen", "orange", "orange", "orangered", "orangered"]
    return colors[level]


def build_search_query(zip_code, min_price, max_price, bed_num):
    # builds a dictionary of query parameters used to pass values into
    # the Location model query
    query_params = {}
    if zip_code:
        # filter based on existence of locations with the specified zip code
        query_params["zipcode"] = zip_code
    if max_price:
        # filter based on existence of apartments  with a rent_price less than or equal (lte)
        # than the max_price
        query_params["apartment_set__rent_price__lte"] = max_price
    if min_price:
        # filter based on existence of apartments  with a rent_price greater than or equal (gte)
        # than the min_price
        query_params["apartment_set__rent_price__gte"] = min_price
    if bed_num:
        # filter based on existence of locations with the specified bedroom number
        query_params["apartment_set__number_of_bed"] = bed_num

    return query_params
