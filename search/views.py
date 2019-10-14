from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

#from craigslist import CraigslistHousing
from craigslist import CraigslistHousing

from .GetRentalHouse import getRentalHouse
from .forms import ZillowSearchForm
from .models import CraigslistLocation
import json
import logging

logger = logging.getLogger(__name__)

class CraigslistIndexView(generic.ListView):
    template_name = 'search/clist_results.html'
    context_object_name = 'cl_results'


def search(request):
    if (request.method == 'POST' and 'zillow' in request.POST):
        form = ZillowSearchForm(request.POST)
        if form.is_valid():
            address = request.POST["address"]
            cityStateZip = request.POST["cityStateZip"]
            rentZestimate = "true"

            jsonData = json.loads(getRentalHouse(address, cityStateZip, rentZestimate))
            results = jsonData['SearchResults:searchresults']['response']['results']['result']
            return render(request, 'search/result.html', {'z_results': results})
    elif (request.method == 'POST' and 'craiglist' in request.POST):
        results = searchCraigslist(request)
        return render(request, 'search/clist_results.html', {'cl_results': results})
   # elif (request.method == 'GET'):
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
    cl_h = CraigslistHousing(site='newyork', area='brk', category='apa',
        filters={'max_price': 2000, 'posted_today': True})
    #for result in cl_h.get_results(sort_by='newest', geotagged='true'):
     #   cl = CraigslistLocation()

    return cl_h.get_results(sort_by='newest')

def clist_results(request):

    cl_h = CraigslistHousing(site='newyork', area='brk', category='apa',
        filters={'max_price': 2000})
    results = cl_h.get_results(sort_by='newest')
    logger.info(f"Type of Resutls List: {type(results)}")
    for r in results:
        logger.info(f"Type of results item: {type(r)}")
    keys = ['a', 'b', 'c']
    """result_string = ''
    for result in results:
        for key in result:
            result_string += f"{key}: {result[key]}"
        result_string += '\n'"""
    #output = ', '.join([r.id for r in results])
    #return HttpResponse(result_string)
    context = { 'clist_results': results,
        'keys': keys }
    return render(request, 'search/clist_results.html', context)
