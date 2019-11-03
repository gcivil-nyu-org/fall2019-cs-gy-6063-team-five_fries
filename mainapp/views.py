from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, "index.html")


@login_required
def account(request):
    return render(request, "account.html", {"user": request.user})

@login_required
def favlist(request):
    favorited_apartments = request.user.favorites.all()
    return render(request, "favlist.html", {"favorited_apartments": favorited_apartments})