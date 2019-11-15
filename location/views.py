from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from review.models import Review
from review.form import ReviewForm
from .forms import ApartmentUploadForm, ClaimForm
from .models import Location, Apartment
from external.cache.zillow import refresh_zillow_housing_if_needed
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib import messages
from external.googleapi.fetch import fetch_geocode
from external.googleapi import g_utils


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
        context["zillow_list"] = self.object.apartment_set.exclude(zpid=None).all()
        context["landlord_list"] = self.object.apartment_set.filter(zpid=None).all()
        if self.request.user.is_authenticated:
            context["can_leave_a_review"] = self.object.check_tenant(self.request.user)
        return context


def apartment_detail_view(request, pk, suite_num):
    apt = Apartment.objects.get(location__id=pk, suite_num=suite_num)

    show_claim_button = not apt.tenant or not apt.landlord
    return render(
        request, "apartment.html", {"apt": apt, "show_claim_button": show_claim_button}
    )


@login_required
def claim_view(request, pk, suite_num):
    apt = Apartment.objects.get(location__id=pk, suite_num=suite_num)

    if request.method == "POST":
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim_type = form.cleaned_data["claim_type"]
            if claim_type == "tenant":
                if apt.tenant:
                    # TODO: note_from_user = form.cleaned_data["note"]
                    pass
                else:
                    apt.tenant = request.user
                    apt.save()
                return render(request, "claim_result.html", {"apt": apt})
            elif claim_type == "landlord":
                if apt.landlord:
                    # TODO: note_from_user = form.cleaned_data["note"]
                    pass
                else:
                    apt.landlord = request.user
                    apt.save()
                return render(request, "claim_result.html", {"apt": apt})
        else:
            return render(request, "claim.html", {"apt": apt, "form": form})
    else:
        form = ClaimForm()
        return render(request, "claim.html", {"apt": apt, "form": form})


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
                content=form.cleaned_data["content"],
                rating=form.cleaned_data["rating"],
            )
            r.save()
    return HttpResponseRedirect(reverse("location", args=(pk,)))


@login_required
def apartment_upload(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = ApartmentUploadForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():

            # process the data in form.cleaned_data as required
            city = form.cleaned_data["city"]
            state = form.cleaned_data["state"]
            address = form.cleaned_data["address"]
            zipcode = form.cleaned_data["zipcode"]
            rent_price = form.cleaned_data["rent_price"]
            image = form.cleaned_data["image"]
            suite_num = form.cleaned_data["suite_num"]
            number_of_bed = form.cleaned_data["number_of_bed"]

            g_data = fetch_geocode(f"{address}, {city} {state}, {zipcode}")

            lat_lng = g_utils.parse_lat_lng(g_data[0])

            # create or retrieve an existing location
            loc, created = Location.objects.get_or_create(
                city=city, state=state, address=address, zipcode=zipcode
            )  # using get_or_create avoids race condition

            if created:
                loc.latitude = lat_lng[0]
                loc.longitude = lat_lng[1]
                loc.save()

            # create an apartment and link it to that location
            apt = Apartment.objects.create(
                suite_num=suite_num,
                number_of_bed=number_of_bed,
                image=image,
                rent_price=rent_price,
                location=loc,
            )

            apt.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse("apartment_upload_confirmation"))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ApartmentUploadForm()

    return render(request, "apartment_upload.html", {"form": form})


def apartment_upload_confirmation(request):
    return render(request, "apartment_upload_confirmation.html")
