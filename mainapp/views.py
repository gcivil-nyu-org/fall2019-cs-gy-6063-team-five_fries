from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.urls import reverse


def index(request):
    return render(request, "index.html")


@login_required
def account(request):
    return render(request, "account.html", {"user": request.user})
