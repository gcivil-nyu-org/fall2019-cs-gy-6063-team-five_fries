from django.test import TestCase
from unittest import mock

from .fetch import fetch_geocode
from .stub import fetch_geocode as fetch_geocode_stub
from .stub import fetch_geocode_response
from .models import (
    GeocodeResponse,
    GeocodeAddressComponent,
    GeocodeGeometry,
    GeocodeLocation,
    GeocodeViewport,
)


class GeocodeTests(TestCase):
    @mock.patch("googlemaps.Client")
    def test_geocode_request(self, mock_requests):
        mock_requests.get().content = fetch_geocode_response()
        fetch_geocode("11103")
        mock_requests.get.assert_called()
        mock_requests.get.assert_called_with()  # pretty sure this is incorrect

    @mock.patch("external.googleapi.fetch.fetch_geocode", fetch_geocode_stub("11103"))
    def test_fetch_geocode(self):
        results = fetch_geocode("11103")
        for result in results:
            self.assertTrue(isinstance(result, GeocodeResponse))

    @mock.patch("external.googleapi.fetch.fetch_geocode", fetch_geocode_stub("11103"))
    def test_value(self):

        results = fetch_geocode("11103")
        precomputed_address1 = GeocodeAddressComponent(
            long_name="11103", short_name="11103", types=["postal_code"]
        )

        precomputed_address2 = GeocodeAddressComponent(
            long_name="Long Island City",
            short_name="LIC",
            types=["neighborhood", "political"],
        )

        precomputed_address3 = GeocodeAddressComponent(
            long_name="Queens",
            short_name="Queens",
            types=["political", "sublocality", "sublocality_level_1"],
        )

        precomputed_address4 = GeocodeAddressComponent(
            long_name="Queens County",
            short_name="Queens County",
            types=["administrative_area_level_2", "political"],
        )

        precomputed_address5 = GeocodeAddressComponent(
            long_name="New York",
            short_name="NY",
            types=["administrative_area_level_1", "political"],
        )

        precomputed_address6 = GeocodeAddressComponent(
            long_name="United States", short_name="US", types=["country", "political"]
        )

        precomputed_loc1 = GeocodeLocation(lat=40.771015, lng=-73.89322)

        precomputed_loc2 = GeocodeLocation(lat=40.753304, lng=-73.92283)

        precomputed_viewport = GeocodeViewport(
            northeast=precomputed_loc1, southwest=precomputed_loc2
        )

        precomputed_loc3 = GeocodeLocation(lat=40.763374, lng=-73.910995)

        precomputed_geometry = GeocodeGeometry(
            location=precomputed_loc3,
            location_type="APPROXIMATE",
            viewport=precomputed_viewport,
        )

        precomputed_response = GeocodeResponse(
            address_components=[
                precomputed_address1,
                precomputed_address2,
                precomputed_address3,
                precomputed_address4,
                precomputed_address5,
                precomputed_address6,
            ],
            formatted_address="Long Island City, NY 11103, USA",
            geometry=precomputed_geometry,
            place_id="ChIJPX80rBRfwokRcw53oIpf_Dc",
            postal="11103",
            postcode_localities=["Astoria", "Long Island City"],
            types=["postal_code"],
        )
        print(results)

        self.assertEqual(results[0], precomputed_response)
