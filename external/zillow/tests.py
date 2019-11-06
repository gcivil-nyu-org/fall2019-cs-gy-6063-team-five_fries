from django.test import TestCase
from .fetch import fetch_zillow_housing, get_zillow_housing
from .stub import fetch_zillow_housing as fetch_zillow_housing_stub
from .stub import get_zillow_response, get_zillow_error_response
from .models import ZillowHousingResponse
from unittest import mock


def get_zws_id_stub():
    return "ZWSID"


class ZillowTests(TestCase):
    @mock.patch("external.zillow.fetch.requests")
    def test_fetch_zillow_housing(self, mock_requests):
        mock_requests.get().content = get_zillow_response()
        fetch_zillow_housing(
            zwsid="dummy", address="Jay St", zipcode="11201", show_rent_z_estimate=True
        )
        mock_requests.get.assert_called()

    @mock.patch("external.zillow.fetch.fetch_zillow_housing", fetch_zillow_housing_stub)
    def test_get_zillow_housing(self):
        results = get_zillow_housing(
            address="Jay St", zipcode="11201", show_rent_z_estimate=True
        )
        for housing in results:
            self.assertTrue(isinstance(housing, ZillowHousingResponse))

    @mock.patch("external.zillow.fetch.get_zws_id", get_zws_id_stub)
    @mock.patch("external.zillow.fetch.requests")
    def test_get_zillow_housing_no_match_results(self, mock_requests):
        """
        In case zillow returns error response, the result of get_zillow_housing should be an empty list
        """
        mock_requests.get().content = get_zillow_error_response()
        results = get_zillow_housing(
            address="Jay St", zipcode="11201", show_rent_z_estimate=True
        )
        self.assertEqual(len(results), 0)
