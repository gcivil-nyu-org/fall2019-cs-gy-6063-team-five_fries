from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.urls import reverse


class LoginView(TemplateView):
    template_name = "login.html"

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))

        else:
            return HttpResponseRedirect(reverse('login'))


def index(request):
    return render(request, 'index.html')
