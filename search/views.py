from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from .getRentalHouse import getRentalHouse
from .forms import SearchForm
import json


#class SearchView(TemplateView):
#    template_name = "search/search.html"

#    def post(self, request, *args, **kwargs):
        #address = request.POST.get('address', False)
        #cityStateZip = request.POST.get('cityStateZip', False)
#        address = request.POST['address']
#        cityStateZip = request.POST['cityStateZip']
#        rentZestimate = "true"

#        request.session['json'] = getRentalHouse(address, cityStateZip, rentZestimate)
#        return render(request, 'result.html', {"json": json})

#def index(request):
#    return render(request,"templates/search.html", {})

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            address = request.POST['address']
            cityStateZip = request.POST['cityStateZip']
            rentZestimate = "true"

            jsonData = json.loads(getRentalHouse(address, cityStateZip, rentZestimate))
            results = jsonData['SearchResults:searchresults']['response']['results']['result']
            return render(request, 'search/result.html', {'results': results})

    else:
        form = SearchForm()
        return render(request, 'search/search.html', {'form': form})


## TODO: Display data beautifully
def result(request):
    return HttpResponse("Result Page")

def error(request):
    return HttpResponse("This is index of Error")
