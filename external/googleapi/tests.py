from django.test import TestCase
from unittest import mock
import attr

from .fetch import fetch_geocode, fetch_reverse_geocode
from .g_utils import (
    parse_lat_lng,
    normalize_us_address,
    get_address,
    get_city,
    get_state,
    get_zipcode,
    get_result,
)
from .stub import fetch_geocode as fetch_geocode_stub
from .stub import fetch_reverse_geocode as fetch_reverse_geocode_stub
from .stub import (
    fetch_geocode_no_zip,
    fetch_reverse_geocode_no_zip,
    fetch_geocode_no_type,
)
from .models import (
    GeocodeResponse,
    GeocodeAddressComponent,
    GeocodeGeometry,
    GeocodeLocation,
    GeocodeViewport,
)
from ..models import CachedSearch


@mock.patch(
    "external.googleapi.fetch.get_google_api_key", mock.MagicMock(return_value="1111")
)
class GeocodeTests(TestCase):
    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_geocode_request(self, mock_client):

        mock_client().geocode = mock.MagicMock()
        _ = fetch_geocode("11103")

        mock_client().geocode.assert_called()
        mock_client().geocode.assert_called_with("11103", None, None, None, None)

    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_fetch_geocode(self, mock_client):

        mock_client().geocode = mock.MagicMock(return_value=fetch_geocode_stub("11103"))
        results = fetch_geocode("11103")

        for result in results:
            self.assertTrue(
                isinstance(GeocodeResponse.from_any(result), GeocodeResponse)
            )

    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_value(self, mock_client):

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
            GeocodeResponse.from_any(precomputed_response),
        )

    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_value_no_zip(self, mock_client):

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
            GeocodeResponse.from_any(precomputed_response),
        )

    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_reverse_geocode_request(self, mock_client):

        mock_client().reverse_geocode = mock.MagicMock()
        _ = fetch_reverse_geocode((40.763374, -73.910995))

        mock_client().reverse_geocode.assert_called()
        mock_client().reverse_geocode.assert_called_with(
            (40.763374, -73.910995), None, None, None
        )

    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_fetch_reverse_geocode(self, mock_client):

        mock_client().reverse_geocode = mock.MagicMock(
            return_value=fetch_reverse_geocode_stub((40.763374, -73.910995))
        )
        results = fetch_reverse_geocode((40.763374, -73.910995))

        for result in results:
            self.assertTrue(
                isinstance(GeocodeResponse.from_any(result), GeocodeResponse)
            )

    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_reverse_geocode_value(self, mock_client):

        self.maxDiff = None
        mock_client().reverse_geocode = mock.MagicMock(
            return_value=fetch_reverse_geocode_stub((40.763374, -73.910995))
        )
        results = fetch_reverse_geocode((40.763374, -73.910995))

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
            GeocodeResponse.from_any(precomputed_response),
        )

    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_reverse_geocode_value_no_zip(self, mock_client):

        self.maxDiff = None

        mock_client().reverse_geocode = mock.MagicMock(
            return_value=fetch_reverse_geocode_no_zip((40.763374, -73.910995))
        )
        results = fetch_reverse_geocode((40.763374, -73.910995))

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
            GeocodeResponse.from_any(precomputed_response),
        )

    @mock.patch("external.googleapi.fetch.googlemaps.Client")
    def test_fetch_geocode_empty_response(self, mock_client):
        """
        Tests the return value of the fetch geocode function
        when google returns an empty array
        """
        mock_client().geocode = mock.MagicMock(return_value=[])

        results = fetch_geocode("11103")
        self.assertListEqual(
            results,
            [],
            msg="fetch_geocode did not return an empty list when it was supposed to",
        )


class GUtilsTests(TestCase):
    def create_search_cache(
        self,
        search_string,
        street="123 Anystreet",
        city="Anytown",
        locality="Anytown",
        state="Anystate",
        zipcode="00000",
        lat=0.0,
        lon=0.0,
    ):
        return CachedSearch.objects.create(
            search_string=search_string,
            street=street,
            city=city,
            locality=locality,
            state=state,
            zipcode=zipcode,
            latitude=lat,
            longitude=lon,
        )

    def test_parse_lat_lng_empty_param(self):
        """
        Tests the parse_lat_lng function with an empty
        parameter
        """
        resp = parse_lat_lng(None)
        self.assertTupleEqual(resp, (None, None), msg="Failed to return an empty tuple")

    def test_parse_lat_lng_valid(self):
        """
        Tests the parse_lat_lng function with valid input
        """
        input = fetch_geocode_stub("1234")
        valid_resp = (40.763374, -73.910995)
        test = parse_lat_lng(input[0])
        self.assertTupleEqual(test, valid_resp, msg="Failed to parse a valid response")

    def test_parse_lat_lng_malformed(self):
        """
        tests the parse_lat_lng function with a malformed response object
        """
        malformed_response = {"geometry": {"lat": 40.763374, "lng": -73.910995}}

        self.assertTupleEqual(parse_lat_lng(malformed_response), (None, None))

    def test_parse_lat_lng_invalid_input(self):
        """
        tests the parse_lat_lng function with an incorrect input
        """
        input = fetch_geocode_stub("1234")
        with self.assertRaises(AttributeError):
            parse_lat_lng(input)

    def test_normalize_no_input(self):
        """
        tests the return value of normalize_us_address with no input
        """
        input = normalize_us_address(address=None)
        self.assertIsNone(input)

    def test_normalize_empty_input(self):
        """
        tests the return value of normalize_us_address with empty input
        """
        input = normalize_us_address(address="")
        self.assertIsNone(input)

    @mock.patch("external.googleapi.g_utils.fetch_geocode")
    def test_normalize_cached_search(self, mock_fetch):
        """
        tests the normalize_us_address function when there is an existing
        cached search
        """
        search_string = "123 USA Street, Anytown, Anystate 00000"
        search_string_norm = " ".join(search_string.split()).lower()
        mock_fetch.return_value = None
        cache = self.create_search_cache(
            search_string=search_string_norm,
            street="123 Anystreet",
            city="Anytown",
            state="Anystate",
            zipcode="00000",
        )
        self.assertEqual(cache.search_string, search_string_norm)
        self.assertEqual(cache.street, "123 Anystreet")
        self.assertEqual(cache.city, "Anytown")
        self.assertEqual(cache.state, "Anystate")
        self.assertEqual(cache.zipcode, "00000")

        normalize_us_address(search_string)
        self.assertFalse(
            mock_fetch.called,
            "the geocode method was called from the normalize_us_address function when it shouldn't have",
        )

    @mock.patch("external.googleapi.g_utils.fetch_geocode")
    def test_normalize_no_cache(self, mock_fetch):
        """
        tests the normalize function when nothing is cached but nothing
        is returned from the api
        """
        search_string = "123 USA Street, Anytown, Anystate 00000"
        search_string_norm = " ".join(search_string.split()).lower()
        search_string_norm += " ny"
        mock_fetch.return_value = None

        input = normalize_us_address(search_string)
        mock_fetch.assert_called_with(search_string_norm, region="us")
        self.assertTrue(
            mock_fetch.called,
            "The fetch_geocode method was not called from the normalize_us_address function when it should have",
        )
        self.assertIsNone(
            input,
            "the normalize_us_address function didn't return None when it was supposed to",
        )

    @mock.patch("external.googleapi.g_utils.fetch_geocode", fetch_geocode_no_type)
    def test_normalize_wrong_state(self):

        result = normalize_us_address("00000")
        self.assertEqual(
            result, None, msg="fetch_geocode did not return None when state wasn't NY"
        )

    @mock.patch("external.googleapi.g_utils.fetch_geocode")
    def test_cache_normalize(self, mock_fetch):
        """
        tests that the cache function is correctly mapping to the same string
        """
        search_string = "123     USA STREET,   AnyTOwn, anySTAte  00000  "
        search_string_norm = "123 usa street, anytown, anystate 00000"
        cache = self.create_search_cache(
            search_string=search_string_norm,
            street="123 USA Street",
            city="Anytown",
            state="Anystate",
            zipcode="00000",
        )
        mock_fetch.return_value = None
        normalize_us_address(search_string)

        self.assertFalse(mock_fetch.called)
        self.assertEqual(
            cache.street, "123 USA Street", "The cached street value was incorrect"
        )
        self.assertEqual(cache.city, "Anytown", "The cached city value was incorrect")
        self.assertEqual(
            cache.state, "Anystate", "The cached state value was incorrect"
        )
        self.assertEqual(
            cache.zipcode, "00000", "The cached zipcode value was incorrect"
        )

    def test_get_address_no_types(self):
        """
        tests the get_address function when the returned result
        has no types field
        """
        address = get_address(fetch_geocode_no_type("00000"))
        self.assertTupleEqual(address, ("", ""))

    def test_get_city_no_types(self):
        """
        tests the get_address function when the returned result
        has no types field
        """
        city, locality = get_city(fetch_geocode_no_type("00000"))
        self.assertEqual(city, None)
        self.assertEqual(locality, None)

    def test_get_state_no_types(self):
        """
        tests the get_address function when the returned result
        has no types field
        """
        state = get_state(fetch_geocode_no_type("00000"))
        self.assertEqual(state, None)

    def test_get_zipcode_no_types(self):
        """
        tests the get_address function when the returned result
        has no types field
        """
        zipcode = get_zipcode(fetch_geocode_no_type("00000"))
        self.assertEqual(zipcode, "")

    def test_get_result_not_dict_or_list(self):

        with self.assertRaises(ValueError) as e:
            get_result("")
        self.assertEqual(str(e.exception), "g_result was neither a list or a dict")

    def test_get_result_empty_list(self):

        result = get_result([])
        self.assertEqual(result, None)
