from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import SearchForm
from location.models import Location

from external.nyc311 import get_311_data
from external.googleapi import normalize_us_address
from external.res import get_res_data
from external.models import NYC311Statistics
from external.cache.nyc311 import refresh_nyc311_statistics_if_needed


def search(request):
    # generic zip code form post
    if request.method == "GET":

        query = {}
        # if there isn't a current search query, check the user session to see
        # if there's a previously stored query
        if request.session.get("last_query", False) and not request.GET.get("query"):

            query["query"] = request.session["last_query"]["query"]
            query["min_price"] = request.session["last_query"]["min_price"]
            query["max_price"] = request.session["last_query"]["max_price"]
            query["bed_num"] = request.session["last_query"]["bed_num"]
        else:
            query["query"] = request.GET.get("query")
            query["min_price"] = request.GET.get("min_price")
            query["max_price"] = request.GET.get("max_price")
            query["bed_num"] = request.GET.get("bed_num")
        # pass the form data to the form class
        search_form = SearchForm(query)

        address = None
        zipcode = None
        if query["query"]:
            address = normalize_us_address(query["query"])
            if address:
                zipcode = address.zipcode

        timeout = False
        max_price = query["max_price"]
        min_price = query["min_price"]
        bed_num = query["bed_num"]

        search_title = ""

        # build the query parameter dictionary that will be used to
        # query the Location model and Apartment model
        query_params_location, query_params_apartment = build_search_query(
            address=address,
            max_price=max_price,
            min_price=min_price,
            bed_num=bed_num,
            orig_query=query["query"],
        )

        # update stored last query in the session object
        request.session["last_query"] = query
        request.session.modified = True

        search_data = {}
        if query_params_location.keys() and search_form.is_valid():

            if address:
                search_title = search_title + f"Address: {address.full_address} "
            if min_price:
                search_title = search_title + f"Min Price: {min_price} "
            if max_price:
                search_title = search_title + f"Max Price: {max_price} "
            if bed_num:
                search_title = search_title + f"Number of Bedroom: {bed_num}"

            search_data["locations"] = Location.objects.filter(
                **query_params_location
            ).distinct()

            # calculate the number of matching apartments at each location
            matching_apartments = {}
            for loc in search_data["locations"]:
                matching_apartments[loc.id] = 0

            # number of apartments at each location satisfying the given criteria
            for loc in search_data["locations"]:
                matches = loc.apartment_set.filter(**query_params_apartment)
                num_matches = matches.count()
                matching_apartments[loc.id] = num_matches

            search_data["matching_apartments"] = matching_apartments

            # paginate the search location results
            page = request.GET.get("page", 1)

            paginator = Paginator(search_data["locations"], 6)
            try:
                locations_page = paginator.page(page)
            except PageNotAnInteger:
                locations_page = paginator.page(1)
            except EmptyPage:
                locations_page = paginator.page(paginator.num_pages)

            search_data["locations_page"] = locations_page

            # Get 311 statistics
            if zipcode:
                try:
                    refresh_nyc311_statistics_if_needed(zipcode)
                    stats = NYC311Statistics.objects.filter(zipcode=zipcode)
                    search_data["stats"] = [
                        (s.complaint_type, 100 * s.complaint_level / 5) for s in stats
                    ]
                    average_complaint_level = sum(
                        s.complaint_level for s in stats
                    ) / len(stats)
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
                "address": address,
                "search_title": search_title,
                "search_form": search_form,
                "timeout": timeout,
                "zipcode": zipcode,
            },
        )
    else:
        # render an error
        search_form = SearchForm()
        return render(request, "search/search.html", {"search_form": search_form})


def data_311(request):
    if request.method == "GET" and "zip_code" in request.GET:
        zip_code = str(request.GET["zip_code"])

        results = {}
        timeout = False
        # Get 311 statistics
        try:
            refresh_nyc311_statistics_if_needed(zip_code)
            results["stats"] = NYC311Statistics.objects.filter(zipcode=zip_code)
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


def build_search_query(address, min_price, max_price, bed_num, orig_query):
    # builds a dictionary of query parameters used to pass values into
    # the Location model query and Apartment model query
    query_params_location = {}
    query_params_apartment = {}

    # Useful for Debugging
    # print(f"address: {address}"
    # f"query: {orig_query}")

    # if the original query, exactly matches the zipcode, we want to only search
    # on the zip code
    if address and address.zipcode and address.zipcode == orig_query:
        query_params_location["zipcode"] = address.zipcode
    elif address:
        # filter based on existence of locations with the specified address
        if address.street:
            query_params_location["address__icontains"] = address.street
        if address.city or address.locality:
            if (
                address.city
                and address.locality
                and address.locality.replace(" ", "").lower()
                in orig_query.replace(" ", "").lower()
            ):
                query_params_location["locality__iexact"] = address.locality
            elif (
                address.city
                and address.city.replace(" ", "").lower()
                in orig_query.replace(" ", "").lower()
            ):  # default to city
                # to include "brooklyn", "Brooklyn" etc. (case-insensitive)
                query_params_location["city__iexact"] = address.city
        if address.state:
            query_params_location["state__iexact"] = address.state
        if address.zipcode:
            query_params_location["zipcode"] = address.zipcode

        # moved here to fix bug when querying "100100" because address returned is None and yet results are displayed
        # rented apartments shouldn't show up in general search
        query_params_location["apartment_set__is_rented"] = False
        query_params_apartment["is_rented"] = False
    if max_price:
        # filter based on existence of apartments  with a rent_price less than or equal (lte)
        # than the max_price
        query_params_location["apartment_set__rent_price__lte"] = max_price
        query_params_apartment["rent_price__lte"] = max_price
    if min_price:
        # filter based on existence of apartments  with a rent_price greater than or equal (gte)
        # than the min_price
        query_params_location["apartment_set__rent_price__gte"] = min_price
        query_params_apartment["rent_price__gte"] = min_price
    if bed_num:
        # filter based on existence of locations with the specified bedroom number
        query_params_location["apartment_set__number_of_bed"] = bed_num
        query_params_apartment["number_of_bed"] = bed_num

    return query_params_location, query_params_apartment


def data_res(request):
    if request.method == "POST":
        zipcode = request.POST["zipcode"]
        try:
            query_results = get_res_data(str(zipcode))
        except TimeoutError:
            return render(request, "search/results_res.html", {"timeout": True})

        return render(
            request,
            "search/results_res.html",
            {"results": query_results, "no_matches": len(query_results) == 0},
        )
    else:
        return render(request, "search/data_res.html", {})
