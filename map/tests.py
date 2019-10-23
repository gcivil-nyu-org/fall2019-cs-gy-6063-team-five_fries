from django.test import TestCase
from .models import CityStreetSpot


class CityStreetSpotTestCase(TestCase):
    def test_picture_url_under_static(self):
        """picture_url should be a url under /static/map/filename"""
        spot = CityStreetSpot.objects.create(
            last_update="2019-10-23 11:21", picture="image.jpg"
        )
        self.assertEqual(spot.picture_url, "/static/map/image.jpg")
