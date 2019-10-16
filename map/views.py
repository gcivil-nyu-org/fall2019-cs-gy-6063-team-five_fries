from django.shortcuts import render


def mapview(request):
    return render(request, "map.html")
