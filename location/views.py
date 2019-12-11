from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.template.loader import get_template
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.forms import modelformset_factory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Location, Apartment, ClaimRequest, OtherImages
from review.models import Review
from review.form import ReviewForm
from .forms import (
    ApartmentUploadForm,
    ClaimForm,
    ContactLandlordForm,
    ApartmentUpdateForm,
    ImageForm,
)
from external.cache.zillow import refresh_zillow_housing_if_needed
from external.googleapi.fetch import fetch_geocode
from external.googleapi import g_utils
from external.cache.nyc311 import refresh_nyc311_statistics_if_needed
from external.models import NYC311Statistics
from external.nyc311 import get_311_data
from django.core.mail import send_mail
from django.conf import settings


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


def apartment_detail_view(request, pk, apk):
    apt = Apartment.objects.get(location__id=pk, id=apk)
    contact_landlord_form = ContactLandlordForm()

    zip_code = None
    if apt:
        zip_code = apt.location.zipcode

    results_311 = {}
    timeout = False
    if zip_code:
        # Get 311 statistics
        try:
            refresh_nyc311_statistics_if_needed(zip_code)
            results_311["stats"] = NYC311Statistics.objects.filter(zipcode=zip_code)
        except TimeoutError:
            timeout = True

    show_claim_button = not apt.tenant or not apt.landlord
    return render(
        request,
        "apartment.html",
        {
            "apt": apt,
            "show_claim_button": show_claim_button,
            "contact_landlord_form": contact_landlord_form,
            "results_311": results_311,
            "timeout": timeout,
        },
    )


def apartment_complaints(request, pk, apk):
    apt = Apartment.objects.get(location__id=pk, id=apk)
    zip_code = None
    if apt:
        zip_code = apt.location.zipcode

    results_311 = {}
    timeout = False
    if zip_code:
        # Get 311 raw complaints
        try:
            results_311["complaints"] = get_311_data(str(zip_code))
        except TimeoutError:
            timeout = True

    # paginate the search location results
    page = request.GET.get("page", 1)

    paginator = Paginator(results_311["complaints"], 6)
    try:
        complaints_page = paginator.page(page)
    except PageNotAnInteger:
        complaints_page = paginator.page(1)
    except EmptyPage:
        complaints_page = paginator.page(paginator.num_pages)

    results_311["complaints_page"] = complaints_page

    return render(
        request,
        "complaints.html",
        {
            "results_311": results_311,
            "timeout": timeout,
            "zip_code": zip_code,
            "apt": apt,
        },
    )


@login_required
def apartment_edit(request, pk, apk):

    object = get_object_or_404(Apartment, location__id=pk, id=apk)
    # if the apartment does not have a landlord or the current user is
    # not the landlord for the apartment, raise a Permission Exception
    if not object.landlord or (object.landlord != request.user):
        raise PermissionDenied

    if request.POST:
        # the 'or None' is necessary in case the files were not updated
        form = ApartmentUpdateForm(request.POST, request.FILES or None, instance=object)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse(
                    "apartment", kwargs={"pk": object.location.id, "apk": object.id}
                )
            )
    else:
        form = ApartmentUpdateForm(instance=object)

    return render(
        request, "apartment_update.html", {"object": object, "apartment_form": form}
    )


@login_required
def apartment_delete(request, pk, apk):

    object = get_object_or_404(Apartment, location__id=pk, id=apk)
    # check permissions
    if not object.landlord or (object.landlord != request.user):
        raise PermissionDenied

    if request.method == "POST":
        object.delete()
        return HttpResponseRedirect(reverse("location", kwargs={"pk": pk}))
    else:
        return HttpResponseRedirect(reverse("apartment", kwargs={"pk": pk, "apk": apk}))


@login_required
def claim_view(request, pk, apk):
    apt = Apartment.objects.get(location__id=pk, id=apk)

    if request.method == "POST":
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim_request = form.save()

            sender_email = settings.EMAIL_HOST_USER
            site = get_current_site(request)

            request_type = form.cleaned_data["request_type"]
            base_uri = request.build_absolute_uri().replace("/claim", "")

            context = {
                "current_site": site,
                "apt": apt,
                "user": claim_request.user,
                "user_name": claim_request.user.full_name,
                "user_email": claim_request.user.email,
                "user_phone": claim_request.user.phone_number,
                "notes": claim_request.note,
                "allow_url": base_uri
                + f"/grant/{claim_request.id}/{claim_request.allow_token}",
                "deny_url": base_uri
                + f"/deny/{claim_request.id}/{claim_request.deny_token}",
            }

            if request_type == "tenant":
                subject = "Tenant Verification Request"
                to = apt.landlord.email
                plaintext = get_template("location/email/tenant_claim_request.txt")

                text_content = plaintext.render(context)

                send_mail(subject, text_content, sender_email, [to])

                messages.success(
                    request,
                    message="Your tenancy request has been submitted.",
                    extra_tags="success",
                )

            elif request_type == "landlord":
                subject = "Apartment Ownership Verification Request"
                user_model = get_user_model()
                admin_list = user_model.objects.filter(is_superuser=True)
                to_list = [user.email for user in admin_list]

                plaintext = get_template("location/email/landlord_claim_request.txt")

                text_content = plaintext.render(context)
                send_mail(subject, text_content, sender_email, to_list)

                messages.success(
                    request,
                    message="Your ownership request has been submitted.",
                    extra_tags="success",
                )

            return HttpResponseRedirect(
                reverse("apartment", kwargs={"pk": pk, "apk": apk})
            )
        else:
            return render(request, "claim.html", {"apt": apt, "form": form})
    else:
        form = ClaimForm(initial={"apartment": apt, "user": request.user})
        return render(request, "claim.html", {"apt": apt, "form": form})


@login_required
def grant_claim(request, pk, apk, id, token):

    apt = get_object_or_404(Apartment, pk=apk)
    claim = get_object_or_404(ClaimRequest, pk=id, apartment=apt, allow_token=token)

    sender_email = settings.EMAIL_HOST_USER
    site = get_current_site(request)
    context = {
        "current_site": site,
        "user_name": claim.user.full_name,
        "apt": apt,
        "location_address": apt.location.full_address,
    }

    if claim.request_type == "tenant":
        if request.user != apt.landlord:
            messages.error(
                request,
                message="You do not have permission to grant tenancy requests.",
                extra_tags="danger",
            )

        else:
            claim.access_granted = True
            claim.save()
            apt.tenant = claim.user
            apt.save()

            subject = "Your Tenancy request has been approved"
            to = claim.user.email

            text_context = get_template("location/email/request_approved.txt")
            context["request_type"] = "tenancy"
            context["approver"] = "landlord"
            message = text_context.render(context)

            send_mail(subject, message, sender_email, [to])

            messages.success(
                request,
                message=f"Granted {claim.user.full_name}'s tenancy request!",
                extra_tags="success",
            )
    elif claim.request_type == "landlord":

        if request.user.is_superuser:
            claim.access_granted = True
            claim.save()

            apt.landlord = claim.user
            apt.save()

            subject = "Your Ownership request has been approved"
            to = claim.user.email

            text_context = get_template("location/email/request_approved.txt")
            context["request_type"] = "ownership"
            context["approver"] = "site administrator"
            message = text_context.render(context)

            send_mail(subject, message, sender_email, [to])

            messages.success(
                request,
                message=f"Granted {claim.user.full_name}'s ownership request!",
                extra_tags="success",
            )
        else:
            messages.error(
                request,
                message="You do not have permission to grant ownership requests.",
                extra_tags="danger",
            )

    return HttpResponseRedirect(reverse("apartment", kwargs={"pk": pk, "apk": apk}))


@login_required
def deny_claim(request, pk, apk, id, token):

    apt = get_object_or_404(Apartment, pk=apk)
    claim = get_object_or_404(ClaimRequest, pk=id, apartment=apt, deny_token=token)
    sender_email = settings.EMAIL_HOST_USER
    site = get_current_site(request)
    context = {
        "current_site": site,
        "user_name": claim.user.full_name,
        "apt": apt,
        "location_address": apt.location.full_address,
    }
    if claim.request_type == "tenant" and request.user == apt.landlord:

        subject = "Your Tenancy request has been rejected"
        to = claim.user.email

        text_context = get_template("location/email/tenant_claim_request_rejected.txt")
        message = text_context.render(context)
        send_mail(subject, message, sender_email, [to])
        messages.error(
            request, message="Tenancy request rejected.", extra_tags="danger"
        )

    elif claim.request_type == "landlord" and request.user.is_superuser:

        subject = "Your Ownership request has been rejected"
        to = claim.user.email

        text_context = get_template(
            "location/email/landlord_claim_request_rejected.txt"
        )
        msg = text_context.render(context)
        send_mail(subject, msg, sender_email, [to])
        messages.error(
            request, message="Ownership request rejected.", extra_tags="danger"
        )
    else:
        messages.error(
            request,
            message="You do not have permission to reject this request.",
            extra_tags="danger",
        )

    return HttpResponseRedirect(reverse("apartment", kwargs={"pk": pk, "apk": apk}))


@login_required
def contact_landlord(request, pk, apk):
    apt = Apartment.objects.get(location__id=pk, id=apk)
    landlord = apt.landlord
    landlord_email = landlord.email
    sender_email = settings.EMAIL_HOST_USER

    if request.method == "POST":
        form = ContactLandlordForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            absolute_url = request.build_absolute_uri().replace("/contact_landlord", "")
            message = (
                f"You were contacted by {request.user.full_name} ({request.user.email}) "
                f"who is interested in your apartment ({absolute_url}). Please find below "
                f"the complete message.\n\nFrom {request.user.full_name}:\n\n"
            )
            message += form.cleaned_data["message"]
            send_mail(
                subject, message, sender_email, [landlord_email], fail_silently=False
            )
            messages.success(
                request, "An email has been sent to the landlord!", extra_tags="success"
            )

    return HttpResponseRedirect(reverse("apartment", kwargs={"pk": pk, "apk": apk}))


@login_required
def favorites(request, pk):
    apartment = get_object_or_404(Location, pk=pk)
    user = request.user
    if apartment not in user.favorites.all():
        user.favorites.add(apartment)
        messages.success(
            request,
            "This apartment has been added to your favorites!",
            extra_tags="success",
        )
    else:
        user.favorites.remove(apartment)
        messages.success(
            request,
            "This apartment has been removed from your favorites!",
            extra_tags="success",
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
    image_form_set = modelformset_factory(OtherImages, form=ImageForm, extra=3)

    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = ApartmentUploadForm(request.POST, request.FILES)
        formset = image_form_set(
            request.POST, request.FILES, queryset=OtherImages.objects.none()
        )

        # check whether it's valid:
        if form.is_valid() and formset.is_valid():

            # process the data in form.cleaned_data as required
            city = form.cleaned_data["city"]
            state = form.cleaned_data["state"]
            address = form.cleaned_data["address"]
            zipcode = form.cleaned_data["zipcode"]
            rent_price = form.cleaned_data["rent_price"]
            image = form.cleaned_data["image"]
            suite_num = form.cleaned_data["suite_num"]
            number_of_bed = form.cleaned_data["number_of_bed"]
            description = form.cleaned_data["description"]

            # retrieve the geocoded data from google
            g_data = fetch_geocode(f"{address}, {city} {state}, {zipcode}")

            # parse out the latitude and longitude from the response
            lat_lng = g_utils.parse_lat_lng(g_data[0])
            street_num, street = g_utils.get_address(g_data[0])
            g_city, g_locality = g_utils.get_city(g_data[0])

            # create or retrieve an existing location
            loc, created = Location.objects.get_or_create(
                city=g_city,
                state=state,
                address=f"{street_num} {street}",
                zipcode=zipcode,
                locality=g_locality,
            )  # using get_or_create avoids race condition

            if created:
                # we add the location here instead of in the get_or_create method
                # due to multiple locations being created from the same address
                # this was happening due to the lat/lng returned from the API sometimes
                # had more digits than what we stored in the DB
                loc.latitude = lat_lng[0]
                loc.longitude = lat_lng[1]
                loc.save()
            elif loc.latitude is None and loc.longitude is None:
                # if the location exists but doesn't have lat/lng values
                # add them
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
                description=description,
                landlord=request.user,
            )
            apt.save()

            # process the data in imgages_form
            for image_form in formset.cleaned_data:
                if "image" in image_form:
                    image = image_form["image"]
                    photo = OtherImages(apartment=apt, image=image)
                    photo.save()

            messages.success(
                request, message="Successfully created Apartment!", extra_tags="success"
            )

            return HttpResponseRedirect(
                reverse("apartment", kwargs={"pk": loc.id, "apk": apt.id})
            )

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ApartmentUploadForm()
        formset = image_form_set(queryset=OtherImages.objects.none())

    return render(request, "apartment_upload.html", {"form": form, "formset": formset})
