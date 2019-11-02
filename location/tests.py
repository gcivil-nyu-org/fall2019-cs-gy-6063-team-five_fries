from django.test import TestCase
from .models import Location


class LocationModelTests(TestCase):
    def test_create_model(self):
        loc = Location.objects.create()
        self.assertIsNotNone(loc)
