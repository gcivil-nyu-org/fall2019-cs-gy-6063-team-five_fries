from django.shortcuts import render
from .forms import SignUpForm


def index(request):
    title = "Sign Up"
    form = SignUpForm(request.POST or None)
    context = {"title": title, "form": form}

    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        context = {"title": "Thank you!"}

    return render(request, "signup/index.html", context)
