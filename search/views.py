from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView


class SearchView(TemplateView):
    template_name = "search/search.html"

    def post(self, request, *args, **kwargs):
        address = request.POST['address']
        cityStateZip = request.POST['cityStateZip']
        rentZestimate = "true"
        return HttpResponseRedirect(reverse('result'))

#def index(request):
#    return render(request,"templates/search.html", {})

def result(request):
    return HttpResponse("This is index of Result")
