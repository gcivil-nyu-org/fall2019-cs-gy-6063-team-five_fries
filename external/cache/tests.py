from django.test import TestCase
from .zillow import refresh_zillow_housing_if_needed
from .nyc311 import refresh_nyc311_statistics_if_needed
from unittest import mock
from ..zillow.stub import fetch_zillow_housing as fetch_zillow_housing_stub
from ..zillow.stub import get_zillow_response
from django.utils import timezone
from location.models import Location, Apartment
import decimal
from ..models import NYC311Statistics


def get_zws_id_stub():
    return "ZWSID"


@mock.patch("external.zillow.fetch.get_zws_id", get_zws_id_stub)
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
            last_estimated=timezone.now(),
            zillow_url="http://www.zillow.com/homes/2094141487_zpid/",
            location=loc,
        )

        refresh_zillow_housing_if_needed(loc)
        actual_request.assert_not_called()

    @mock.patch("external.zillow.fetch.requests")
    def test_cache_remove_outdated(self, mock_requests):
        """
        `refresh_if_needed` should remove outdated apartments for a location
        which are not included in the latest zillow response
        """

        zillow_response = get_zillow_response("zillow-normal.xml")
        mock_requests.get().content = zillow_response
        result_count = zillow_response.count("<zpid>")

        loc = Location.objects.create(
            city="Brooklyn",
            state="NY",
            address="33 Bond St",
            zipcode="11201",
            latitude=decimal.Decimal("40.688563"),
            longitude=decimal.Decimal("-73.983519"),
        )

        Apartment.objects.create(
            suite_num="999",
            zpid="zpid-that-is-not-included-in-the-response",
            estimated_rent_price=2865,
            last_estimated=timezone.now(),
            zillow_url="http://www.zillow.com/homes/2094141487_zpid/",
            location=loc,
        )

        # 1. # apt with zpid = 1
        self.assertEqual(loc.apartment_set.exclude(zpid=None).count(), 1)

        # 2. refresh_zillow_housing_if_needed should
        # - add zillow information in the response (+result_count)
        # - reset the outdated zillow information (-1)
        refresh_zillow_housing_if_needed(loc)

        # 3. # apt with zpid = result_count (= 1 + result_count - 1)
        self.assertEqual(loc.apartment_set.exclude(zpid=None).count(), result_count)


class NYC311StatisticsCacheTests(TestCase):
    @mock.patch("external.cache.nyc311.get_311_statistics")
    def test_fetch(self, get_311_statistics):
        """
        `refresh_if_needed` should make an actual request
        if there is no cached data
        """
        self.assertEqual(NYC311Statistics.objects.filter(zipcode="11201").count(), 0)
        refresh_nyc311_statistics_if_needed("11201")
        get_311_statistics.assert_called()

    @mock.patch("external.cache.nyc311.get_311_statistics")
    def test_cache(self, get_311_statistics):
        """
        `refresh_if_needed` should not call get_311_statistics if there is up-to-date cached data
        """

        NYC311Statistics.objects.create(
            zipcode="11201",
            complaint_type="",
            complaint_level=0,
            total_complaints_query_zip=0,
            closed_complaints_query_zip=0,
            percentage_complaints_closed=0,
            max_complaints=0,
            max_complaints_zip="11201",
        )
        refresh_nyc311_statistics_if_needed("11201")
        get_311_statistics.assert_not_called()
