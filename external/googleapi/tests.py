from django.test import TestCase
from unittest import mock
import attr

from .fetch import fetch_geocode
from .stub import fetch_geocode as fetch_geocode_stub
from .stub import fetch_geocode_no_zip
from .models import (
    GeocodeResponse,
    GeocodeAddressComponent,
    GeocodeGeometry,
    GeocodeLocation,
    GeocodeViewport,
)


@mock.patch(
    "external.googleapi.fetch.get_google_api_key", mock.MagicMock(return_value="1111")
)
class GeocodeTests(TestCase):
    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_geocode_request(self, mock_client):
        # mock_secret = mock.MagicMock(return_value="1111")
        mock_client().geocode = mock.MagicMock()
        _ = fetch_geocode("11103")

        mock_client().geocode.assert_called()
        mock_client().geocode.assert_called_with("11103", None, None, None, None)

    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_fetch_geocode(self, mock_client):
        # mock_secret = mock.MagicMock(return_value="1111")
        mock_client().geocode = mock.MagicMock(return_value=fetch_geocode_stub("11103"))
        results = fetch_geocode("11103")

        for result in results:
            self.assertTrue(
                isinstance(GeocodeResponse.get_converter(result), GeocodeResponse)
            )

    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_value(self, mock_client):
        # mock_secret = mock.MagicMock(return_value="1111")
        self.maxDiff = None
        mock_client().geocode = mock.MagicMock(return_value=fetch_geocode_stub("11103"))
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

        precomputed_address7 = GeocodeAddressComponent(
            long_name="28-15", short_name="28-15", types=["street_number"]
        )

        precomputed_address8 = GeocodeAddressComponent(
            long_name="34th Street", short_name="34th St", types=["route"]
        )

        precomputed_loc1 = GeocodeLocation(lat=40.771015, lng=-73.89322)

        precomputed_loc2 = GeocodeLocation(lat=40.753304, lng=-73.92283)

        precomputed_viewport = GeocodeViewport(
            northeast=precomputed_loc1, southwest=precomputed_loc2
        )

        precomputed_loc3 = GeocodeLocation(lat=40.763374, lng=-73.910995)

        precomputed_geometry = GeocodeGeometry(
            bounds=precomputed_viewport,
            location=precomputed_loc3,
            location_type="APPROXIMATE",
            viewport=precomputed_viewport,
        )

        precomputed_response = GeocodeResponse(
            address_components=[
                precomputed_address7,
                precomputed_address8,
                precomputed_address1,
                precomputed_address2,
                precomputed_address3,
                precomputed_address4,
                precomputed_address5,
                precomputed_address6,
            ],
            formatted_address="28-15 34th St, Long Island City, NY 11103, USA",
            geometry=precomputed_geometry,
            place_id="ChIJPX80rBRfwokRcw53oIpf_Dc",
            postal="11103",
            postcode_localities=["Astoria", "Long Island City"],
            types=["postal_code"],
        )

        self.assertEqual(GeocodeResponse(**results[0]), precomputed_response)
        self.assertDictEqual(results[0], attr.asdict(precomputed_response))
        self.assertEqual(
            GeocodeResponse(**results[0]),
            GeocodeResponse.get_converter(precomputed_response),
        )

    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_value_no_zip(self, mock_client):
        # mock_secret = mock.MagicMock(return_value="1111")
        self.maxDiff = None

        mock_client().geocode = mock.MagicMock(
            return_value=fetch_geocode_no_zip("11103")
        )
        results = fetch_geocode("11103")

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

        precomputed_address7 = GeocodeAddressComponent(
            long_name="28-15", short_name="28-15", types=["street_number"]
        )

        precomputed_address8 = GeocodeAddressComponent(
            long_name="34th Street", short_name="34th St", types=["route"]
        )

        precomputed_loc1 = GeocodeLocation(lat=40.771015, lng=-73.89322)

        precomputed_loc2 = GeocodeLocation(lat=40.753304, lng=-73.92283)

        precomputed_viewport = GeocodeViewport(
            northeast=precomputed_loc1, southwest=precomputed_loc2
        )

        precomputed_loc3 = GeocodeLocation(lat=40.763374, lng=-73.910995)

        precomputed_geometry = GeocodeGeometry(
            bounds=precomputed_viewport,
            location=precomputed_loc3,
            location_type="APPROXIMATE",
            viewport=precomputed_viewport,
        )

        precomputed_response = GeocodeResponse(
            address_components=[
                precomputed_address7,
                precomputed_address8,
                precomputed_address2,
                precomputed_address3,
                precomputed_address4,
                precomputed_address5,
                precomputed_address6,
            ],
            formatted_address="28-15 34th St, Long Island City, NY 11103, USA",
            geometry=precomputed_geometry,
            place_id="ChIJPX80rBRfwokRcw53oIpf_Dc",
            postal="",
            postcode_localities=["Astoria", "Long Island City"],
            types=["postal_code"],
        )

        self.assertEqual(GeocodeResponse(**results[0]), precomputed_response)
        self.assertDictEqual(results[0], attr.asdict(precomputed_response))
        self.assertEqual(
            GeocodeResponse(**results[0]),
            GeocodeResponse.get_converter(precomputed_response),
        )
