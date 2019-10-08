from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.http import Http404


class LoginView(TemplateView):
    template_name = "login.html"

    def post(self, request, *args, **kwargs):
        raise Http404("not implemented")


def index(request):
    return render(request, 'index.html')
