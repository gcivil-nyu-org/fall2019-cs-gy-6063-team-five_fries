from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("search"))
    else:
        return render(request, "index.html")


def account(request):
    if request.user.is_authenticated:
        return render(request, "account.html", {"user": request.user})
    else:
        return HttpResponseRedirect(reverse("login"))


def search(request):
    return HttpResponseRedirect(reverse("search"))
