from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView

#from craigslist import CraigslistHousing
import cragslist

from .GetRentalHouse import getRentalHouse
from .forms import ZillowSearchForm
import json


def search(request):
    if request.method == 'POST':
        form = ZillowSearchForm(request.POST)
        if form.is_valid():
            address = request.POST["address"]
            cityStateZip = request.POST["cityStateZip"]
            rentZestimate = "true"

            jsonData = json.loads(getRentalHouse(address, cityStateZip, rentZestimate))
            results = jsonData['SearchResults:searchresults']['response']['results']['result']
            return render(request, 'search/result.html', {'z_results': results})
    #elif (request.method == 'GET'):
    #    return HttpResponse(searchCraigslist(request), content_type="application/json")
    else:
        ## render an error
        form = ZillowSearchForm()
        return render(request, 'search/search.html', {'form': form})


# TODO: Display data beautifully
def result(request):
    return HttpResponse("Result Page")


def error(request):
    return HttpResponse("This is index of Error")


def searchCraigslist(request):
    '''
    does a default search against craigslist
    '''
    #cl_h = {'test': 'test'}#CraigslistHousing(site='newyork', area='brk', category='apa',
        #filters={'max_price': 2000})
        

    return {}
