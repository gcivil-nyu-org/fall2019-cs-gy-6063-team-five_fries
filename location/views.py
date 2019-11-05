from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime

from review.models import Review
from review.form import ReviewForm
from .models import Location


class LocationView(generic.DetailView):
    model = Location
    template_name = "location.html"

    def get_context_data(self, **kwargs):
        context = super(LocationView, self).get_context_data(**kwargs)
        context["form"] = ReviewForm
        return context


@login_required
def review(request, pk):
    if request.method == "POST":
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
