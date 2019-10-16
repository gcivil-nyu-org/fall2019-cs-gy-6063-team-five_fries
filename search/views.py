from django.shortcuts import render
from django.http import HttpResponse
from .GetRentalHouse import getRentalHouse
from .forms import SearchForm
import json
from data_311.get_311_data import get_311_data


def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            address = request.POST["address"]
            cityStateZip = request.POST["cityStateZip"]
            rentZestimate = "true"

            jsonData = json.loads(getRentalHouse(address, cityStateZip, rentZestimate))
            results = jsonData["SearchResults:searchresults"]["response"]["results"][
                "result"
            ]
            return render(request, "search/result.html", {"results": results})

    else:
        form = SearchForm()
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
