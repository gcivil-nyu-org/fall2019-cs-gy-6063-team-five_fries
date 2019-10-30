from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, "mainapp/index.html")


@login_required
def account(request):
    return render(request, "account.html", {"user": request.user})


def search(request):
    return HttpResponseRedirect(reverse("search"))
