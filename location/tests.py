from django.test import TestCase
from django.urls import reverse
from django.conf import settings

# from django.core import mail
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from unittest import mock

import string

from .models import Location, Apartment, ClaimRequest, OtherImages
from .forms import ClaimForm
from mainapp.models import SiteUser
from review.models import Review
from external.zillow.stub import fetch_zillow_housing
from external.googleapi.stub import fetch_geocode as fetch_geocode_stub
from external.nyc311.stub import fetch_311_data as fetch_311_data_stub


def create_location_and_apartment(
    address="1234 Coney Island Avenue",
    city="Bushwick",
    locality="Brooklyn",
    state="New York",
    zipcode=11218,
    suite_num="18C",
    number_of_bed=3,
    image="Images/System_Data_Flow_Diagram.png",
    rent_price=3000,
):

    # using get_or_create avoids race condition
    loc = Location.objects.get_or_create(
        city=city, state=state, address=address, zipcode=zipcode, locality=locality
    )[0]

    # create an apartment and link it to that location
    apt = Apartment.objects.create(
        suite_num=suite_num,
        number_of_bed=number_of_bed,
        image=image,
        rent_price=rent_price,
        location=loc,
    )

    return loc, apt


def create_second_apartment(
    location,
    suite_num="19C",
    number_of_bed=2,
    image="Images/System_Data_Flow_Diagram.png",
    rent_price=2500,
):
    apt2 = Apartment.objects.create(
        suite_num=suite_num,
        number_of_bed=number_of_bed,
        image=image,
        rent_price=rent_price,
        location=location,
    )
    return apt2


def create_claim_request(user, apartment, request_type="tenant"):
    return ClaimRequest.objects.create(
        user=user, apartment=apartment, request_type=request_type, note="Note"
    )


class LocationModelTests(TestCase):
    fixtures = ["locations.json"]

    def test_create_model(self):
        loc = Location.objects.create()
        self.assertIsNotNone(loc)

    def test_google_map_url(self):
        loc = Location.objects.get(pk=1)
        self.assertTrue(
            "https://www.google.com/maps/search/?api=1&" in loc.google_map_url
        )

        # https://developers.google.com/maps/documentation/urls/url-encoding#special-characters
        accepted_chars = "".join(
            [string.ascii_letters, string.digits, "-_.~", "!*'();:@&=+$,/?%#[]"]
        )
        for c in loc.google_map_url:
            self.assertTrue(c in accepted_chars)

    def test_avg_rate(self):
        s1 = SiteUser.objects.create(full_name="test_user")
        l1 = Location.objects.create(state="NY")
        r1 = Review.objects.create(
            location=l1, user=s1, content="test_content", rating=1
        )
        r2 = Review.objects.create(
            location=l1, user=s1, content="test_content2", rating=5
        )
        avg = (r1.rating + r2.rating) / 2
        self.assertEqual(l1.avg_rate(), avg)

    def test_empty_review_avg_rate(self):
        l1 = Location.objects.create(state="NY")
        self.assertEqual(l1.avg_rate(), 0)


@mock.patch(
    "external.googleapi.fetch.get_google_api_key", mock.MagicMock(return_value="1111")
)
@mock.patch("external.zillow.fetch.fetch_zillow_housing", fetch_zillow_housing)
class LocationViewTests(TestCase):
    fixtures = ["locations.json"]

    def test_location_view(self):
        response = self.client.get(reverse("location", args=(1,)))
        self.assertEqual(response.status_code, 200)

    def test_favorites_list_view(self):
        self.client.force_login(SiteUser.objects.create(username="testuser"))
        response = self.client.get(reverse("favlist"))
        self.assertEqual(response.status_code, 200)

    def test_review_view(self):
        self.client.force_login(SiteUser.objects.get_or_create(username="testuser")[0])
        response = self.client.get(reverse("review", args=(1,)))
        self.assertEqual(response.status_code, 302)

    def test_is_not_tenant(self):
        loc = Location.objects.get(pk=1)
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)

        # user is not a tenant
        self.assertFalse(loc.check_tenant(user))

        response = self.client.get(reverse("location", args=(1,)))
        self.assertNotContains(response, "Write something")

    def test_is_tenant(self):
        loc = Location.objects.get(pk=1)
        apt = Apartment.objects.create(location=loc)
        user = SiteUser.objects.create(username="testuser")

        apt.tenant = user
        apt.save()
        self.client.force_login(user)

        # user is a tenant
        self.assertTrue(loc.check_tenant(user))

        response = self.client.get(reverse("location", args=(1,)))
        self.assertContains(response, "Review")

    def test_apartment_view(self):
        """create location and apartment associated with that location.
        test checks if the apartment detail view is loaded"""
        loc, apt = create_location_and_apartment()

        response = self.client.get(
            reverse("apartment", kwargs={"pk": loc.id, "apk": apt.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_location_upload_not_logged_in(self):
        """
        tests a GET response against the apartment_upload page
        while not logged in
        """
        response = self.client.get(reverse("apartment_upload"))
        self.assertRedirects(
            response, "/accounts/login/?next=/location/apartment_upload"
        )

    def test_location_upload_logged_in(self):
        """
        tests a GET requests against the apartment_upload page while
        logged in
        """
        self.client.force_login(SiteUser.objects.create(username="testuser"))
        response = self.client.get(reverse("apartment_upload"))
        self.assertEqual(response.status_code, 200)

    @mock.patch("location.forms.fetch_geocode", fetch_geocode_stub)
    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_location_upload_post(self, mock_client):
        """
        tests a POST against the apartment_upload page while
        logged in as a landlord
        """
        mock_client().geocode = mock.MagicMock(return_value=fetch_geocode_stub("11103"))

        self.client.force_login(SiteUser.objects.create(username="testuser"))

        # Create a fake image
        im = Image.new(mode="RGB", size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, "JPEG")
        im_io.seek(0)
        mem_image = InMemoryUploadedFile(
            im_io, None, "image.jpg", "image/jpeg", len(im_io.getvalue()), None
        )

        post_data = {
            "city": "Long Island City",
            "state": "NY",
            "address": "28-15 34th Street",
            "zipcode": "11103",
            "suite_num": "1",
            "rent_price": 2500,
            "number_of_bed": 1,
            "description": "This is a test",
            "image": mem_image,
            "form-TOTAL_FORMS": 3,
            "form-INITIAL_FORMS": 0,
        }

        response = self.client.post(reverse("apartment_upload"), post_data)
        self.assertRedirects(response, reverse("apartment", kwargs={"pk": 7, "apk": 8}))

    @mock.patch("location.forms.fetch_geocode", fetch_geocode_stub)
    @mock.patch("location.views.fetch_geocode", fetch_geocode_stub)
    def test_location_upload_location_capitalization(self):
        """
        Tests to make sure when uploading apartments, an apartment
        is associated with the correct location even if the location
        capitalization differs slightly
        """
        self.client.force_login(SiteUser.objects.create(username="testuser"))

        loc, apa = create_location_and_apartment(
            address="28-15 34th Street",
            city="Long Island City",
            locality="Queens",
            state="NY",
            zipcode="11103",
            suite_num="1C",
            number_of_bed=1,
            rent_price=3000,
        )

        # Create a fake image
        im = Image.new(mode="RGB", size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, "JPEG")
        im_io.seek(0)
        mem_image = InMemoryUploadedFile(
            im_io, None, "image.jpg", "image/jpeg", len(im_io.getvalue()), None
        )

        post_data = {
            "city": "long Island city",
            "state": "NY",
            "address": "28-15 34TH Street",
            "zipcode": "11103",
            "suite_num": "1",
            "rent_price": 2500,
            "number_of_bed": 1,
            "description": "This is a test",
            "image": mem_image,
            "form-TOTAL_FORMS": 3,
            "form-INITIAL_FORMS": 0,
        }

        self.client.post(reverse("apartment_upload"), post_data)

        apa_created = Apartment.objects.filter(
            suite_num=post_data["suite_num"], rent_price=post_data["rent_price"]
        ).exists()
        self.assertTrue(apa_created, msg="Apartment was not created successfully")

        locs_count = Location.objects.filter(
            city__iexact="Long Island City", locality="Queens", zipcode=11103
        ).count()
        self.assertEqual(
            locs_count, 1, msg="Duplicate location should not have been created"
        )

    @mock.patch("location.views.fetch_geocode", fetch_geocode_stub)
    @mock.patch("location.forms.fetch_geocode", fetch_geocode_stub)
    def test_location_upload_negative_price(self):
        """
        tests uploading an apartment that has a negative rental price
        """
        self.client.force_login(SiteUser.objects.create(username="testuser"))

        # Create a fake image
        im = Image.new(mode="RGB", size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, "JPEG")
        im_io.seek(0)
        mem_image = InMemoryUploadedFile(
            im_io, None, "image.jpg", "image/jpeg", len(im_io.getvalue()), None
        )

        post_data = {
            "city": "New York",
            "state": "NY",
            "address": "111 anytown st",
            "zipcode": "10003",
            "suite_num": "1",
            "rent_price": -2500,
            "number_of_bed": 1,
            "description": "This is a test",
            "image": mem_image,
            "form-TOTAL_FORMS": 3,
            "form-INITIAL_FORMS": 0,
        }

        response = self.client.post(reverse("apartment_upload"), post_data)
        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response, "Ensure this value is greater than or equal to 1."
        )

    @mock.patch("location.forms.fetch_geocode", mock.MagicMock(return_value=[]))
    def test_location_upload_no_location(self):
        """
        insures a validation error is raised when an apartment is uploaded
        that does not have a corresponding location in the google API
        """
        self.client.force_login(SiteUser.objects.create(username="testuser"))

        # Create a fake image
        im = Image.new(mode="RGB", size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, "JPEG")
        im_io.seek(0)
        mem_image = InMemoryUploadedFile(
            im_io, None, "image.jpg", "image/jpeg", len(im_io.getvalue()), None
        )

        post_data = {
            "city": "Test",
            "state": "AK",
            "address": "123 test ave",
            "zipcode": "99999",
            "suite_num": "1",
            "rent_price": 2500,
            "number_of_bed": 1,
            "description": "This is a test",
            "image": mem_image,
            "form-TOTAL_FORMS": 3,
            "form-INITIAL_FORMS": 0,
        }
        response = self.client.post(reverse("apartment_upload"), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Unable to locate that address, please check that it was entered correctly.",
        )

    @mock.patch("location.forms.fetch_geocode", fetch_geocode_stub)
    def test_location_upload_negative_suite(self):
        """
        insures a validation error is raised when an apartment is uploaded
        that does not have a corresponding location in the google API
        """
        self.client.force_login(SiteUser.objects.create(username="testuser"))

        # Create a fake image
        im = Image.new(mode="RGB", size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, "JPEG")
        im_io.seek(0)
        mem_image = InMemoryUploadedFile(
            im_io, None, "image.jpg", "image/jpeg", len(im_io.getvalue()), None
        )

        post_data = {
            "city": "Test",
            "state": "AK",
            "address": "123 test ave",
            "zipcode": "99999",
            "suite_num": "-1",
            "rent_price": 2500,
            "number_of_bed": 1,
            "description": "This is a test",
            "image": mem_image,
            "form-TOTAL_FORMS": 3,
            "form-INITIAL_FORMS": 0,
        }
        response = self.client.post(reverse("apartment_upload"), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "You cannot submit an apartment with a negative Suite Number"
        )

    def test_location_edit_not_logged_in(self):
        """
        Tests the 'apartment_edit' page redirects when the user is not logged in
        """
        loc, apt = create_location_and_apartment()
        response = self.client.get(
            reverse("apartment_edit", kwargs={"pk": loc.id, "apk": apt.id})
        )
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/location/{loc.id}/apartment/{apt.id}/edit",
        )

    def test_location_edit_no_landlord(self):
        """
        Tests the 'apartment_edit' page when a user is logged in but
        the apartment doesn't have a landlord
        """

        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        loc, apt = create_location_and_apartment()
        apt.landlord = None
        apt.save()

        response = self.client.get(
            reverse("apartment_edit", kwargs={"pk": loc.id, "apk": apt.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_location_edit_not_landlord(self):
        """
        Tests the 'apartment_edit' page when a user is logged in
        but is not the apartments landlord
        """
        user = SiteUser.objects.create(username="testuser")
        landlord = SiteUser.objects.create(username="landlord")
        self.client.force_login(user)
        loc, apt = create_location_and_apartment()
        apt.landlord = landlord
        apt.save()

        response = self.client.get(
            reverse("apartment_edit", kwargs={"pk": loc.id, "apk": apt.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_location_edit_landlord(self):
        """
        tests the 'apartment_edit' page when a user is logged in
        and is the landlord of the apartment
        """
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        loc, apt = create_location_and_apartment()
        apt.landlord = user
        apt.save()

        response = self.client.get(
            reverse("apartment_edit", kwargs={"pk": loc.id, "apk": apt.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_location_edit_post(self):
        """
        tests a successful POST request to the 'apartment_edit' URI
        """
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        loc, apt = create_location_and_apartment()
        apt.landlord = user
        apt.save()

        form_data = {
            "suite_num": apt.suite_num,
            "rent_price": 2500,
            "number_of_bed": 2,
            "description": "A different description",
        }
        response = self.client.post(
            reverse("apartment_edit", kwargs={"pk": loc.id, "apk": apt.id}), form_data
        )
        # insure the valid edit redirects successfully to the apartment page
        self.assertRedirects(
            response, reverse("apartment", kwargs={"pk": loc.id, "apk": apt.id})
        )

    def test_location_edit_num(self):
        """
        tests a POST request to the 'apartment_edit' URI where the suite_num
        matches an existing apartment
        """
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        loc, apt = create_location_and_apartment()
        apt2 = create_second_apartment(loc)
        apt.landlord = user
        apt2.landlord = user
        apt.save()
        apt2.save()

        form_data = {
            "suite_num": apt2.suite_num,
            "rent_price": 2500,
            "number_of_bed": 2,
            "description": "a different description",
        }
        response = self.client.post(
            reverse("apartment_edit", kwargs={"pk": loc.id, "apk": apt.id}), form_data
        )
        # insure that it returns to the edit page due to validation failures
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Another apartment exists at that location with that Suite number.",
        )

    def test_location_edit_num_negative(self):
        """
        tests a POST request to the 'apartment_edit' URI where the suite_num
        is negative
        """
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        loc, apt = create_location_and_apartment()
        apt.landlord = user
        apt.save()

        form_data = {
            "suite_num": -1,
            "rent_price": 2500,
            "number_of_bed": 2,
            "description": "a different description",
        }
        response = self.client.post(
            reverse("apartment_edit", kwargs={"pk": loc.id, "apk": apt.id}), form_data
        )
        # insure that it returns to the edit page due to validation failures
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "You cannot submit an apartment with a negative Suite Number"
        )

    def test_location_edit_num_succcess(self):
        """
        tests a POST request to the 'apartment_edit' URI where the suite_num
        matches an existing apartment
        """
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        loc, apt = create_location_and_apartment()
        apt2 = create_second_apartment(loc)
        apt.landlord = user
        apt2.landlord = user
        apt.save()
        apt2.save()

        form_data = {
            "suite_num": "20C",
            "rent_price": 2500,
            "number_of_bed": 2,
            "description": "a different description",
        }
        response = self.client.post(
            reverse("apartment_edit", kwargs={"pk": loc.id, "apk": apt.id}), form_data
        )
        # insure the valid number change redirects successfully to the new edit page
        self.assertRedirects(
            response, reverse("apartment", kwargs={"pk": loc.id, "apk": apt.id})
        )

    def test_apartment_delete_not_logged_in(self):
        """
        Tests the apartments delete function when the user is not logged in
        """
        loc, apa = create_location_and_apartment()
        response = self.client.post(
            reverse("apartment_delete", kwargs={"pk": loc.id, "apk": apa.id}), {}
        )
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/location/{loc.id}/apartment/{apa.id}/delete",
        )

    def test_apartment_delete_no_landlord(self):
        """
        Tests the apartment delete function when the apartment doesn't have a
        landlord
        """

        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        loc, apa = create_location_and_apartment()
        response = self.client.post(
            reverse("apartment_delete", kwargs={"pk": loc.id, "apk": apa.id}), {}
        )
        self.assertEqual(response.status_code, 403)

    def test_apartment_delete_dif_landlord(self):
        """
        tests the apartment delete when the current user is not the landlord of the building
        """
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        landlord = SiteUser.objects.create(username="landlord")
        loc, apa = create_location_and_apartment()
        apa.landlord = landlord
        apa.save()
        response = self.client.post(
            reverse("apartment_delete", kwargs={"pk": loc.id, "apk": apa.id}), {}
        )
        self.assertEqual(response.status_code, 403)

    def test_apartment_delete_get(self):
        """
        tests the apartment delete when it receives a GET instead of a POST
        """
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        loc, apa = create_location_and_apartment()
        apa.landlord = user
        apa.save()
        response = self.client.get(
            reverse("apartment_delete", kwargs={"pk": loc.id, "apk": apa.id})
        )
        self.assertRedirects(
            response, reverse("apartment", kwargs={"pk": loc.id, "apk": apa.id})
        )

    def test_apartment_delete(self):
        """
        tests a successful delete
        """
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        loc, apa = create_location_and_apartment()
        apa.landlord = user
        apa.save()
        response = self.client.post(
            reverse("apartment_delete", kwargs={"pk": loc.id, "apk": apa.id}), {}
        )
        self.assertFalse(
            Apartment.objects.filter(location__id=loc.id, id=apa.id).exists(),
            msg="Apartment wasn't deleted",
        )
        self.assertRedirects(response, reverse("location", kwargs={"pk": loc.id}))

    def test_apartment_delete_no_apartment(self):
        """
        insures that a 404 is thrown if the apartment doesn't exist
        """
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        loc, apa = create_location_and_apartment()
        id = apa.id
        apa.delete()
        response = self.client.post(
            reverse("apartment_delete", kwargs={"pk": loc.id, "apk": id}), {}
        )
        self.assertEqual(response.status_code, 404)

    def test_contact_landlord_not_logged_in(self):
        """
        tests a GET response against the contact_landlord page
        while not logged in
        """
        loc, apt = create_location_and_apartment()

        response = self.client.get(
            reverse("contact_landlord", kwargs={"pk": loc.id, "apk": apt.id})
        )

        redirect_url = f"/accounts/login/?next=/location/{loc.id}/apartment/{apt.id}/contact_landlord"

        self.assertRedirects(response, redirect_url)

    def test_contact_landlord_logged_in(self):
        """
        tests a GET response against the contact_landlord page
        while logged in
        """
        loc, apt = create_location_and_apartment()
        user = SiteUser.objects.create(
            username="testuser", email=settings.EMAIL_HOST_USER
        )
        self.client.force_login(user)
        apt.landlord = user
        apt.save()
        response = self.client.get(
            reverse("contact_landlord", kwargs={"pk": loc.id, "apk": apt.id})
        )

        self.assertRedirects(
            response, reverse("apartment", kwargs={"pk": loc.id, "apk": apt.id})
        )

    def test_display_interested_if_not_landlord(self):
        loc, apt = create_location_and_apartment()
        response = self.client.get(
            reverse("apartment", kwargs={"pk": loc.id, "apk": apt.id})
        )
        soup = BeautifulSoup(response.content, "html.parser")
        content = soup.get_text()
        self.assertIn("Interested?", content)

    def test_display_interested_if_landlord_and_renter_same(self):
        loc, apt = create_location_and_apartment()
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        apt.landlord = user
        apt.save()
        response = self.client.get(
            reverse("apartment", kwargs={"pk": loc.id, "apk": apt.id})
        )
        soup = BeautifulSoup(response.content, "html.parser")
        content = soup.get_text()
        self.assertIn("Interested?", content)

    def test_display_interested_if_landlord_and_renter_different(self):
        loc, apt = create_location_and_apartment()
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        landlord = SiteUser.objects.create(username="landlord")
        apt.landlord = landlord
        apt.save()
        response = self.client.get(
            reverse("apartment", kwargs={"pk": loc.id, "apk": apt.id})
        )
        soup = BeautifulSoup(response.content, "html.parser")
        content = soup.get_text()
        self.assertIn("Interested?", content)

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data_stub)
    def test_apartment_complaints(self):
        """
        Tests the apartment complaints page
        """
        loc, apa = create_location_and_apartment()
        response = self.client.post(
            reverse("complaints", kwargs={"pk": loc.id, "apk": apa.id}), {}
        )
        self.assertContains(response, "311 Data Complaints")


@mock.patch("location.views.settings", mock.MagicMock(return_value="site@mail.com"))
class ClaimViewTests(TestCase):
    fixtures = ["locations.json"]

    def test_200_if_logged_in(self):
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        apa = Apartment.objects.get(location__id=6, suite_num="2R")
        response = self.client.get(reverse("claim", args=(6, apa.id)))
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("claim", args=(6, 1)))
        self.assertEqual(response.status_code, 302)

    def test_form_submit_tenant_without_note(self):
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        apa = Apartment.objects.get(location__id=6, suite_num="2R")
        apa.landlord = SiteUser.objects.create(username="landlord")
        apa.save()

        post_data = {"user": user, "apartment": apa, "request_type": "tenant"}

        response = self.client.post(reverse("claim", args=(6, apa.id)), post_data)
        claim = ClaimRequest.objects.filter(apartment=apa).exists()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(claim, msg="Should not have created a claim")

    def test_form_submit_tenant_with_note(self):

        user = SiteUser.objects.create(username="testuser", email="test@test.com")
        self.client.force_login(user)
        apa = Apartment.objects.get(location__id=6, suite_num="2R")
        apa.landlord = SiteUser.objects.create(username="landlord")
        apa.save()
        # mock_mailer = mock.MagicMock()
        post_data = {
            "user": user.id,
            "apartment": apa.id,
            "request_type": "tenant",
            "note": "Please approve my request",
        }

        response = self.client.post(reverse("claim", args=(6, apa.id)), post_data)
        # self.assertTrue(mock_mailer.send_mail.called, msg="send_mail should have been called")

        # self.assertEqual(len(mail.outbox), 1, msg="Should have sent an email out")
        created = ClaimRequest.objects.filter(apartment=apa).exists()
        self.assertTrue(created, msg="Should have created a claim")
        self.assertRedirects(
            response,
            reverse("apartment", kwargs={"pk": apa.location.id, "apk": apa.id}),
        )

    def test_form_submit_landlord_without_note(self):
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        apa = Apartment.objects.get(location__id=6, suite_num="2R")

        post_data = {"user": user, "apartment": apa, "request_type": "landlord"}

        response = self.client.post(reverse("claim", args=(6, apa.id)), post_data)
        claim = ClaimRequest.objects.filter(apartment=apa).exists()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(claim, msg="Should not have created a claim")

    @mock.patch("location.views.send_mail")
    def test_form_submit_landlord_with_note(self, mock_mailer):

        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        apa = Apartment.objects.get(location__id=6, suite_num="2R")

        post_data = {
            "user": user.id,
            "apartment": apa.id,
            "request_type": "landlord",
            "note": "Please approve my request",
        }

        response = self.client.post(reverse("claim", args=(6, apa.id)), post_data)

        created = ClaimRequest.objects.filter(apartment=apa).exists()

        self.assertTrue(created, msg="Should have created a claim")
        # mock_mailer.send_mail.assert_called()
        self.assertRedirects(
            response,
            reverse("apartment", kwargs={"pk": apa.location.id, "apk": apa.id}),
        )

    def test_form_submit_invalid(self):
        user = SiteUser.objects.create(username="testuser")
        self.client.force_login(user)
        apa = Apartment.objects.get(location__id=6, suite_num="2R")

        response = self.client.post(
            reverse("claim", args=(6, apa.id)),
            {"claim_type": "HAHAHA", "note": "Please approve my request"},
        )
        claim = ClaimRequest.objects.filter(apartment=apa).exists()
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "successful")
        self.assertFalse(claim, msg="Should not have created a claim")


@mock.patch("location.views.send_mail")
class GrantClaimTests(TestCase):
    def test_grant_not_logged_in(self, mock_mailer):
        loc, apa = create_location_and_apartment()
        user = SiteUser.objects.create_user(username="user", email="test@teest.com")
        claim_request = create_claim_request(user=user, apartment=apa)

        response = self.client.get(
            reverse(
                "grant_claim",
                args=(loc.id, apa.id, claim_request.id, claim_request.allow_token),
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_grant_tenant_no_landlord(self, mock_mailer):
        loc, apa = create_location_and_apartment()
        user = SiteUser.objects.create_user(username="user", email="test@teest.com")
        landlord = SiteUser.objects.create_user(
            username="landlord", email="test@teest.com"
        )
        apa.landlord = landlord
        apa.save()
        self.client.force_login(user)
        claim_request = create_claim_request(user=user, apartment=apa)

        response = self.client.get(
            reverse(
                "grant_claim",
                args=(loc.id, apa.id, claim_request.id, claim_request.allow_token),
            ),
            follow=True,  # tells client to follow the request through the redirect
        )

        self.assertEqual(response.status_code, 200)

        claim = ClaimRequest.objects.get(pk=claim_request.id)
        self.assertFalse(claim.access_granted, msg="Claim should not have been granted")
        self.assertRedirects(response, reverse("apartment", args=(loc.id, apa.id)))

        message = list(response.context.get("messages"))[0]
        self.assertTrue(
            "danger" in message.tags,
            msg="There should have been a error message raised",
        )
        self.assertTrue(
            "You do not have permission to grant tenancy requests." in message.message,
            msg="Should have raised a permission warning",
        )

    def test_grant_tenant(self, mock_mailer):
        loc, apa = create_location_and_apartment()
        user = SiteUser.objects.create_user(
            username="user", email="test@teest.com", full_name="user"
        )
        apa.landlord = user
        apa.save()
        self.client.force_login(user)
        claim_request = create_claim_request(user=user, apartment=apa)

        response = self.client.get(
            reverse(
                "grant_claim",
                args=(loc.id, apa.id, claim_request.id, claim_request.allow_token),
            ),
            follow=True,  # tells client to follow the request through the redirect
        )
        self.assertEqual(
            response.status_code, 200, msg="Initial response should have returned 200"
        )
        claim = ClaimRequest.objects.get(pk=claim_request.id)
        self.assertTrue(claim.access_granted, msg="Claim should have been granted")
        self.assertRedirects(response, reverse("apartment", args=(loc.id, apa.id)))

        message = list(response.context.get("messages"))[0]
        self.assertTrue(
            "success" in message.tags, msg="Message should have a success tag"
        )
        self.assertTrue(
            f"Granted {user.full_name}'s tenancy request!" in message.message,
            msg="Should have displayed a success message",
        )

    def test_grant_landlord_not_admin(self, mock_mailer):
        loc, apa = create_location_and_apartment()
        user = SiteUser.objects.create_user(username="user", email="test@teest.com")
        landlord = SiteUser.objects.create_user(
            username="landlord", email="test@teest.com"
        )
        apa.landlord = landlord
        apa.save()
        self.client.force_login(user)
        claim_request = create_claim_request(
            user=user, apartment=apa, request_type="landlord"
        )

        response = self.client.get(
            reverse(
                "grant_claim",
                args=(loc.id, apa.id, claim_request.id, claim_request.allow_token),
            ),
            follow=True,  # tells the client to follow the request through the redirect
        )

        self.assertEqual(
            response.status_code, 200, msg="Initial request should return 200"
        )

        claim = ClaimRequest.objects.get(pk=claim_request.id)
        self.assertFalse(claim.access_granted, msg="Claim should not have been granted")
        self.assertRedirects(response, reverse("apartment", args=(loc.id, apa.id)))

        message = list(response.context.get("messages"))[0]
        self.assertTrue(
            "danger" in message.tags,
            msg="There should have been a error message raised",
        )
        self.assertTrue(
            "You do not have permission to grant ownership requests."
            in message.message,
            msg="Should have raised a permission warning",
        )

    def test_grant_landlord(self, mock_mailer):
        loc, apa = create_location_and_apartment()
        user = SiteUser.objects.create_user(
            username="user", email="test@teest.com", full_name="user"
        )
        admin = SiteUser.objects.create_user(username="admin", is_superuser=True)
        apa.landlord = user
        apa.save()
        self.client.force_login(admin)
        claim_request = create_claim_request(
            user=user, apartment=apa, request_type="landlord"
        )

        response = self.client.get(
            reverse(
                "grant_claim",
                args=(loc.id, apa.id, claim_request.id, claim_request.allow_token),
            ),
            follow=True,  # tells the client to follow the request through the redirect
        )
        self.assertEqual(
            response.status_code, 200, msg="Initial request should have returned 200"
        )

        claim = ClaimRequest.objects.get(pk=claim_request.id)
        self.assertTrue(claim.access_granted, msg="Claim should have been granted")
        self.assertRedirects(response, reverse("apartment", args=(loc.id, apa.id)))

        message = list(response.context.get("messages"))[0]
        self.assertTrue(
            "success" in message.tags, msg="Message should have a success tag"
        )
        self.assertTrue(
            f"Granted {claim.user.full_name}'s ownership request!" in message.message,
            msg="Should have displayed a success message",
        )


@mock.patch("location.views.send_mail")
class DenyClaimTests(TestCase):
    def test_deny_not_logged_in(self, mock_mailer):
        loc, apa = create_location_and_apartment()
        user = SiteUser.objects.create_user(username="user", email="test@teest.com")
        claim_request = create_claim_request(user=user, apartment=apa)

        response = self.client.get(
            reverse(
                "deny_claim",
                args=(loc.id, apa.id, claim_request.id, claim_request.deny_token),
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_deny_tenant_not_landlord(self, mock_mailer):
        loc, apa = create_location_and_apartment()
        user = SiteUser.objects.create_user(username="user")
        self.client.force_login(user)
        claim_request = create_claim_request(user=user, apartment=apa)
        apa.landlord = SiteUser.objects.create_user(username="landlord")
        apa.save()

        response = self.client.get(
            reverse(
                "deny_claim",
                args=(loc.id, apa.id, claim_request.id, claim_request.deny_token),
            ),
            follow=True,  # tells the client to follow the request through the redirect
        )
        self.assertEqual(
            response.status_code, 200, msg="Initial request should have returned a 200"
        )

        claim = ClaimRequest.objects.get(pk=claim_request.id)
        self.assertFalse(claim.access_granted)
        self.assertRedirects(response, reverse("apartment", args=(loc.id, apa.id)))

        message = list(response.context.get("messages"))[0]
        self.assertTrue(
            "danger" in message.tags,
            msg="There should have been a error message raised",
        )
        self.assertTrue(
            "You do not have permission to reject this request." in message.message,
            msg="Should have raised a permission warning",
        )

    def test_deny_tenant_not_admin(self, mock_mailer):
        loc, apa = create_location_and_apartment()
        user = SiteUser.objects.create_user(username="user")
        self.client.force_login(user)
        claim_request = create_claim_request(
            user=user, apartment=apa, request_type="landlord"
        )
        apa.landlord = SiteUser.objects.create_user(username="landlord")
        apa.save()

        response = self.client.get(
            reverse(
                "deny_claim",
                args=(loc.id, apa.id, claim_request.id, claim_request.deny_token),
            ),
            follow=True,  # tells the client to follow the request through the redirect
        )
        self.assertEqual(
            response.status_code, 200, msg="Initial request should have returned a 200"
        )

        claim = ClaimRequest.objects.get(pk=claim_request.id)
        self.assertFalse(claim.access_granted)
        self.assertRedirects(response, reverse("apartment", args=(loc.id, apa.id)))

        message = list(response.context.get("messages"))[0]
        self.assertTrue(
            "danger" in message.tags,
            msg="There should have been a error message raised",
        )
        self.assertTrue(
            "You do not have permission to reject this request." in message.message,
            msg="Should have raised a permission warning",
        )

    def test_deny_tenant(self, mock_mailer):
        loc, apa = create_location_and_apartment()
        user = SiteUser.objects.create_user(username="user")
        apa.landlord = user
        apa.save()
        claim_request = create_claim_request(user=user, apartment=apa)

        self.client.force_login(user)
        response = self.client.get(
            reverse(
                "deny_claim",
                args=(loc.id, apa.id, claim_request.id, claim_request.deny_token),
            ),
            follow=True,  # tells the client to follow the request through the redirect
        )
        self.assertEqual(
            response.status_code, 200, msg="Initial request should have returned a 200"
        )

        claim = ClaimRequest.objects.get(pk=claim_request.id)
        self.assertFalse(claim.access_granted)
        self.assertRedirects(response, reverse("apartment", args=(loc.id, apa.id)))

        message = list(response.context.get("messages"))[0]
        self.assertTrue(
            "danger" in message.tags,
            msg="There should have been a error message raised",
        )
        self.assertTrue(
            "Tenancy request rejected." in message.message,
            msg="Should have raised a permission warning",
        )

    def test_deny_landlord(self, mock_mailer):
        loc, apa = create_location_and_apartment()
        user = SiteUser.objects.create_user(username="user", is_superuser=True)
        apa.landlord = user
        apa.save()
        claim_request = create_claim_request(
            user=user, apartment=apa, request_type="landlord"
        )

        self.client.force_login(user)
        response = self.client.get(
            reverse(
                "deny_claim",
                args=(loc.id, apa.id, claim_request.id, claim_request.deny_token),
            ),
            follow=True,  # tells the client to follow the request through the redirect
        )
        self.assertEqual(
            response.status_code, 200, msg="Initial request should have returned a 200"
        )

        claim = ClaimRequest.objects.get(pk=claim_request.id)
        self.assertFalse(claim.access_granted)
        self.assertRedirects(response, reverse("apartment", args=(loc.id, apa.id)))

        message = list(response.context.get("messages"))[0]
        self.assertTrue(
            "danger" in message.tags,
            msg="There should have been a error message raised",
        )
        self.assertTrue(
            "Ownership request rejected." in message.message,
            msg="Should have raised a permission warning",
        )


class ClaimFormTests(TestCase):
    def test_empty_forms(self):
        form = ClaimForm({})
        self.assertFalse(form.is_valid(), msg="An empty for should not be valid")

    def test_not_empty_form(self):
        user = SiteUser.objects.create_user(username="user", email="test@test.com")
        landlord = SiteUser.objects.create_user(
            username="landlord", email="landlord@test.com"
        )
        loc, apt = create_location_and_apartment()
        apt.landlord = landlord
        apt.save()

        data = {
            "user": user.id,
            "apartment": apt.id,
            "request_type": "tenant",
            "note": "Please approve my request",
        }

        form = ClaimForm(data)
        self.assertTrue(form.is_valid())

    def test_form_no_note(self):
        user = SiteUser.objects.create_user(username="user", email="test@test.com")
        loc, apt = create_location_and_apartment()

        data = {"user": user.id, "apartment": apt.id, "request_type": "tenant"}
        form = ClaimForm(data)
        self.assertFalse(
            form.is_valid(), msg="Claim form without a note should not be valid."
        )

    def test_form_no_type(self):
        user = SiteUser.objects.create_user(username="user", email="test@test.com")
        loc, apt = create_location_and_apartment()

        data = {"user": user.id, "apartment": apt.id, "note": "Note"}
        form = ClaimForm(data)
        self.assertFalse(
            form.is_valid(), msg="Claim form without a type should not be valid."
        )

    def test_form_invalid_type(self):
        user = SiteUser.objects.create_user(username="user", email="test@test.com")
        loc, apt = create_location_and_apartment()

        data = {
            "user": user.id,
            "apartment": apt.id,
            "request_type": "superman",
            "note": "Please approve",
        }
        form = ClaimForm(data)
        self.assertFalse(
            form.is_valid(), msg="Claim form with an invalid type should not be valid."
        )

    def test_tenant_request_no_landlord(self):
        user = SiteUser.objects.create_user(username="user", email="test@test.com")
        loc, apt = create_location_and_apartment()

        data = {
            "user": user.id,
            "apartment": apt.id,
            "request_type": "tenant",
            "note": "Please approve my request",
        }

        form = ClaimForm(data)
        self.assertFalse(
            form.is_valid(),
            msg="ClaimForm should not be valid for tenant requests without a landlord",
        )

    def test_picture_url_without_http(self):

        loc, apt = create_location_and_apartment()

        # Create a fake image
        im = Image.new(mode="RGB", size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, "JPEG")
        im_io.seek(0)
        mem_image = InMemoryUploadedFile(
            im_io, None, "image.jpg", "image/jpeg", len(im_io.getvalue()), None
        )

        img = OtherImages.objects.create(apartment=apt, image=mem_image)

        self.assertRegexpMatches(img.picture_url, r"/media/.+\.jpg")

    def test_picture_url_with_http(self):
        loc, apt = create_location_and_apartment()

        http_image = "http://craigslist.org/example.jpg"

        img = OtherImages.objects.create(apartment=apt, image=http_image)

        self.assertEqual(img.picture_url, "http://craigslist.org/example.jpg")

    def test_picture_url_without_img(self):
        loc, apt = create_location_and_apartment()

        img = OtherImages.objects.create(apartment=apt)

        self.assertEqual(img.picture_url, None)
