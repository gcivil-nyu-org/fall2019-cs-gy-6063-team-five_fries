from django.test import TestCase
from django.urls import reverse
from datetime import datetime
from .models import Location, Apartment
from mainapp.models import SiteUser
from review.models import Review
import string
from unittest import mock
from external.zillow.stub import fetch_zillow_housing


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
            location=l1, user=s1, content="test_content", time=datetime.now(), rating=1
        )
        r2 = Review.objects.create(
            location=l1, user=s1, content="test_content2", time=datetime.now(), rating=5
        )
        avg = (r1.rating + r2.rating) / 2
        self.assertEqual(l1.avg_rate(), avg)

    def test_empty_review_avg_rate(self):
        l1 = Location.objects.create(state="NY")
        self.assertEqual(l1.avg_rate(), 0)


@mock.patch("external.zillow.fetch.fetch_zillow_housing", fetch_zillow_housing)
class LocationViewTests(TestCase):
    fixtures = ["locations.json"]

    def test_location_view(self):
        response = self.client.get(reverse("location", args=(1,)))
        self.assertEqual(response.status_code, 200)

    def test_favorites_list_view(self):
        self.client.force_login(
            SiteUser.objects.create(user_type="R", username="testuser")
        )
        response = self.client.get(reverse("favlist"))
        self.assertEqual(response.status_code, 200)

    def test_review_view(self):
        self.client.force_login(SiteUser.objects.get_or_create(username="testuser")[0])
        response = self.client.get(reverse("review", args=(1,)))
        self.assertEqual(response.status_code, 302)

    def test_is_not_tanant(self):
        self.client.force_login(
            SiteUser.objects.create(user_type="R", username="testuser")
        )
        response = self.client.get(reverse("location", args=(1,)))
        self.assertNotContains(response, "Write something")

    def test_is_tanant(self):
        self.client.force_login(
            SiteUser.objects.create(user_type="T", username="testuser")
        )
        response = self.client.get(reverse("location", args=(1,)))
        self.assertContains(response, "Write something")

    def test_apartment_view(self):
        """create location and apartment associated with that location.
        test checks if the apartment detail view is loaded"""
        city = "Brooklyn"
        state = "New York"
        address = "1234 Coney Island Avenue"
        zipcode = 11218
        # using get_or_create avoids race condition
        loc = Location.objects.get_or_create(
            city=city, state=state, address=address, zipcode=zipcode
        )[0]

        # create an apartment and link it to that location
        suite_num = "18C"
        number_of_bed = 3
        image = "Images/System_Data_Flow_Diagram.png"
        rent_price = 3000
        apt = Apartment.objects.create(
            suite_num=suite_num,
            number_of_bed=number_of_bed,
            image=image,
            rent_price=rent_price,
            location=loc,
        )

        response = self.client.get(
            reverse("apartment", kwargs={"pk": loc.id, "suite_num": apt.suite_num})
        )
        self.assertEqual(response.status_code, 200)
