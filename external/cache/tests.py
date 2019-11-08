from django.test import TestCase
from .zillow import refresh_zillow_housing_if_needed
from unittest import mock
from ..zillow.stub import fetch_zillow_housing as fetch_zillow_housing_stub
from django.utils import timezone
from location.models import Location, Apartment
import decimal


class ZillowTests(TestCase):
    fixtures = ["locations.json"]

    @mock.patch("external.zillow.fetch.fetch_zillow_housing")
    def test_fetch(self, actual_request):
        """
        `refresh_if_needed` should make an actual request
        if there is no cached data
        """
        loc = Location.objects.create(
            city="Brooklyn",
            state="NY",
            address="33 Bond St",
            zipcode="11201",
            latitude=decimal.Decimal("40.688563"),
            longitude=decimal.Decimal("-73.983519"),
        )
        sample_response = fetch_zillow_housing_stub(
            address=loc.address,
            city_state=f"{loc.city} {loc.state}",
            show_rent_z_estimate=True,
        )
        actual_request.return_value = sample_response

        self.assertEqual(
            Apartment.objects.filter(location__address=loc.address).count(), 0
        )
        refresh_zillow_housing_if_needed(loc)
        actual_request.assert_called()
        self.assertTrue(
            Apartment.objects.filter(location__address=loc.address).count() > 0
        )
        self.assertNotEqual(loc.last_fetched_zillow, None)

    @mock.patch("external.cache.zillow.get_zillow_housing")
    def test_cache(self, actual_request):
        """
        `refresh_if_needed` should not make an actual request and
        return the cached data if there is up-to-date cached data
        """
        loc = Location.objects.create(
            city="Brooklyn",
            state="NY",
            address="33 Bond St",
            zipcode="11201",
            latitude=decimal.Decimal("40.688563"),
            longitude=decimal.Decimal("-73.983519"),
            last_fetched_zillow=timezone.now(),
        )

        Apartment.objects.create(
            zpid="2094141487",
            estimated_rent_price=2865,
            estimated_rent_price_currency="USD",
            last_estimated=timezone.now(),
            zillow_url="http://www.zillow.com/homes/2094141487_zpid/",
            location=loc,
        )

        refresh_zillow_housing_if_needed(loc)
        actual_request.assert_not_called()
