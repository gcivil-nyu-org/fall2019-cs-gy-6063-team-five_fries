from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime

from review.models import Review
from review.form import ReviewForm
from .models import Location
from external.cache.zillow import refresh_zillow_housing_if_needed
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib import messages


class LocationView(generic.DetailView):
    model = Location
    template_name = "location.html"

    def get_object(self):
        obj = super().get_object()
        refresh_zillow_housing_if_needed(obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super(LocationView, self).get_context_data(**kwargs)
        context["form"] = ReviewForm()
        return context


@login_required
def favorites(request, pk):
    apartment = get_object_or_404(Location, pk=pk)
    user = request.user
    if apartment not in user.favorites.all():
        user.favorites.add(apartment)
        messages.success(request, "This apartment has been added to your favorites!")
    else:
        user.favorites.remove(apartment)
        messages.success(
            request, "This apartment has been removed from your favorites!"
        )
    return HttpResponseRedirect(reverse("location", args=(pk,)))


@login_required
def favlist(request):
    favorited_apartments = request.user.favorites.all()
    return render(
        request, "favlist.html", {"favorited_apartments": favorited_apartments}
    )


@login_required
def review(request, pk):
    if "form_submit" in request.POST:
        form = ReviewForm(request.POST)
        if form.is_valid():
            r = Review(
                user=request.user,
                location=Location.objects.only("id").get(id=pk),
                content=request.POST["content"],
                time=datetime.now(),
            )
            r.save()
    return HttpResponseRedirect(reverse("location", args=(pk,)))
