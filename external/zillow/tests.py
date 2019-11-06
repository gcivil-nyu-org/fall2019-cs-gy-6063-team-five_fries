from django.test import TestCase
from .fetch import fetch_zillow_housing, get_zillow_housing
from .stub import get_all_zillow_response
from .models import ZillowHousingResponse
from unittest import mock


def get_zws_id_stub():
    return "ZWSID"


class ZillowTests(TestCase):
    @mock.patch("external.zillow.fetch.requests")
    def test_fetch_zillow_housing(self, mock_requests):
        for zillow_response in get_all_zillow_response():
            mock_requests.get().content = zillow_response
            fetch_zillow_housing(
                zwsid="dummy",
                address="Jay St",
                zipcode="11201",
                show_rent_z_estimate=True,
            )
            mock_requests.get.assert_called()

    @mock.patch("external.zillow.fetch.get_zws_id", get_zws_id_stub)
    @mock.patch("external.zillow.fetch.requests")
    def test_get_zillow_housing(self, mock_requests):
        """
        In case zillow returns error response, the result of get_zillow_housing should be an empty list
        """
        for zillow_response in get_all_zillow_response():
            mock_requests.get().content = zillow_response
            results = get_zillow_housing(
                address="Jay St", zipcode="11201", show_rent_z_estimate=True
            )

            self.assertEqual(len(results), zillow_response.count("<zpid>"))
            for housing in results:
                self.assertTrue(isinstance(housing, ZillowHousingResponse))
