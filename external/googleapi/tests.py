from django.test import TestCase
from unittest import mock
import attr

from .fetch import fetch_geocode
from .stub import fetch_geocode as fetch_geocode_stub
from .stub import fetch_geocode_response, MOCK_DATA
from .models import (
    GeocodeResponse,
    GeocodeAddressComponent,
    GeocodeGeometry,
    GeocodeLocation,
    GeocodeViewport,
)


class GeocodeTests(TestCase):
    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_geocode_request(self, mock_client):
        # mock_client.get().content = fetch_geocode_response()
        mock_client().geocode = mock.MagicMock()
        # mock_requests.geocode.assert_called_with(address="11103")
        _ = fetch_geocode("11103")
        # mock_client.get.assert_called()
        mock_client().geocode.assert_called()
        mock_client().geocode.assert_called_with(
            address="11103"
        )  # pretty sure this is incorrect

    @mock.patch(
        "external.googleapi.tests.fetch_geocode", side_effect=fetch_geocode_stub
    )
    def test_fetch_geocode(self, mock_geocode):
        # mock_geocode.geocode = mock.MagicMock(return_value=MOCK_DATA)
        results = fetch_geocode("11103")
        print(f"test_fetch_geocode RESULTS: {results}")
        for result in results:
            self.assertTrue(
                isinstance(GeocodeResponse.from_dict(result), GeocodeResponse)
            )

    @mock.patch(
        "external.googleapi.tests.fetch_geocode", side_effect=fetch_geocode_stub
    )
    def test_value(self, mock_geocode):
        self.maxDiff = None
        # mock_geocode.geocode = mock.MagicMock(return_value=MOCK_DATA)
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
            # bounds=precomputed_viewport,
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
            place_id="ChIJ_eoztkBfwokRJZ8i8DXMYfI",
            postal="11103",
            postcode_localities=["Astoria", "Long Island City"],
            types=["postal_code"],
        )

        print(f"results[0]: {results[0]}")
        print(f"precomputed: {attr.asdict(precomputed_response)}")
        self.assertDictEqual(results[0], attr.asdict(precomputed_response))
        # resp = GeocodeResponse.from_dict(results[0])
        # self.assertEqual(resp, precomputed_response)
