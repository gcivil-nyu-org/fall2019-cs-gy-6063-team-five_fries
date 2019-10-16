from django.shortcuts import render

def mapview(request):
    return render(request, "map.html")


# TODO: Display data beautifully
def search(request):
    return HttpResponse("Result Page")
# Create your views here.
