from .forms import SignUpForm
from django.views.generic.edit import FormView
from django.shortcuts import render


class IndexView(FormView):
    template_name = "signup/index.html"
    form_class = SignUpForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def back(request):
        return render(request, "index.html")
