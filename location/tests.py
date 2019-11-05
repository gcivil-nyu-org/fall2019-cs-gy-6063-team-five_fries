from django.test import TestCase
from django.urls import reverse
from .models import Location
from mainapp.models import SiteUser
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


class LocationViewTests(TestCase):
    fixtures = ["locations.json"]

    @mock.patch("external.zillow.fetch.fetch_zillow_housing", fetch_zillow_housing)
    def test_location_view(self):
        response = self.client.get(reverse("location", args=(1,)))
        self.assertEqual(response.status_code, 200)

    def test_favorites_list_view(self):
        self.client.force_login(
            SiteUser.objects.create(user_type="R", username="testuser")
        )
        response = self.client.get(reverse("favlist"))
        self.assertEqual(response.status_code, 200)
