from django.test import TestCase
from django.urls import reverse
from unittest import mock

from external.models import Address
from location.models import Location, Apartment
from external.nyc311.stub import fetch_311_data
from external.googleapi.stub import fetch_geocode as fetch_geocode_stub
from external.res.stub import fetch_res_data
from .templatetags.custom_tags import get_item, get_modulo
from .views import build_search_query


def create_location_and_apartment():
    city = "Brooklyn"
    state = "New York"
    address = "1234 Coney Island Avenue"
    zipcode = 11218
    # using get_or_create avoids race condition
    loc = Location.objects.get_or_create(
        city=city, state=state, address=address, zipcode=zipcode
    )[0]

    # create an apartment and link it to that location
    suite_num = "18C"
    number_of_bed = 3
    image = "Images/System_Data_Flow_Diagram.png"
    rent_price = 3000
    apt = Apartment.objects.create(
        suite_num=suite_num,
        number_of_bed=number_of_bed,
        image=image,
        rent_price=rent_price,
        location=loc,
    )

    return loc, apt


@mock.patch("external.googleapi.g_utils.fetch_geocode", fetch_geocode_stub)
class SearchIndexViewTests(TestCase):
    def test_search_index(self):
        """
        Tests the index page, insuring the navigational buttons
        are rendered
        """
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search All Locations")
        self.assertContains(response, "Address")
        self.assertContains(response, "Go")

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data)
    @mock.patch("external.res.fetch.fetch_res_data", fetch_res_data)
    def test_search_index_with_query(self):
        """
        Tests the search page being retrieved with a query passed in
        """
        response = self.client.get("/search/?query=10000")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search results")
        self.assertContains(response, "Address:")

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data)
    @mock.patch("external.res.fetch.fetch_res_data", fetch_res_data)
    def test_search_index_no_query(self):
        """
        tests the search page with an incomplete query passed in
        """
        response = self.client.get("/search/?query=")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Address:")

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data)
    @mock.patch("external.res.fetch.fetch_res_data", fetch_res_data)
    def test_search_page_query_only(self):
        """
        tests the search page with only a query passed in
        """
        response = self.client.get("/search/?query=10000")
        self.assertContains(response, "Address:")
        self.assertNotContains(response, "Max Price:")
        self.assertNotContains(response, "Min Price:")

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data)
    @mock.patch("external.res.fetch.fetch_res_data", fetch_res_data)
    def test_search_page_min_price(self):
        """
        tests the search page with query and min_price passed in
        """
        response = self.client.get("/search/?query=NY&min_price=500")
        self.assertContains(response, "Address:")
        self.assertNotContains(response, "Max Price:")
        self.assertContains(response, "Min Price: 500")

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data)
    @mock.patch("external.res.fetch.fetch_res_data", fetch_res_data)
    def test_search_page_max_price(self):
        """
        tests the search page with query and max_price passed in
        """
        response = self.client.get("/search/?query=NY&min_price=&max_price=2000")
        self.assertContains(response, "Address:")
        self.assertContains(response, "Max Price: 2000")
        self.assertNotContains(response, "Min Price:")

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data)
    @mock.patch("external.res.fetch.fetch_res_data", fetch_res_data)
    def test_search_page_bed_num(self):
        """
        tests the search page with query and bed_num passed in
        """
        response = self.client.get("/search/?query=NY&min_price=&max_price=&bed_num=4")
        self.assertContains(response, "Address:")
        self.assertContains(response, "Number of Bedroom: 4")
        self.assertNotContains(response, "Max Price:")
        self.assertNotContains(response, "Min Price:")

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data)
    @mock.patch("external.res.fetch.fetch_res_data", fetch_res_data)
    def test_search_page_all_params(self):
        response = self.client.get(
            "/search/?query=NY&min_price=500&max_price=2000&bed_num=4"
        )
        self.assertContains(response, "Address:")
        self.assertContains(response, "Max Price: 2000")
        self.assertContains(response, "Min Price: 500")
        self.assertContains(response, "Number of Bedroom: 4")

    def test_search_reversed_price(self):
        response = self.client.get(
            "/search/?query=NY&min_price=2000&max_price=500&bed_num=4"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Larger than Max")
        self.assertContains(response, "Less than Min")

    @mock.patch("search.views.normalize_us_address")
    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data)
    def test_search_page_matching_apartments(self, mock_norm):
        """
        tests to make sure that "matching apartments" is displayed for each location
        in the search results
        """
        mock_norm.return_value = Address(
            street="",
            city="Brooklyn",
            state="New York",
            zipcode=11218,
            latitude=0.0,
            longitude=0.0,
        )
        loc, apa = create_location_and_apartment()
        response = self.client.get("/search/?query=Brooklyn%2C+New+York+11218")

        self.assertContains(response, "Matching Apartments:")

    @mock.patch("search.views.normalize_us_address")
    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data)
    def test_search_rented_apartment(self, mock_norm):
        """
        tests to make sure that apartments that have been marked as rented don't show up in
        the general search
        """
        mock_norm.return_value = Address(
            street="",
            city="Brooklyn",
            state="New York",
            zipcode=11218,
            latitude=0.0,
            longitude=0.0,
        )
        loc, apa = create_location_and_apartment()
        response = self.client.get("/search/?query=Brooklyn%2C+New+York+11218")
        self.assertEqual(
            len(response.context["search_data"]["locations"]),
            1,
            msg="Did not return result when it should have",
        )

        apa.is_rented = True
        apa.save()

        # once an apartment has been rented, it should no longer show up in the default search
        response = self.client.get("/search/?query=Brooklyn%2C+New+York+11218")
        self.assertEqual(
            len(response.context["search_data"]["locations"]),
            0,
            msg="Returned results when it shouldn't have",
        )

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data)
    @mock.patch("external.res.fetch.fetch_res_data", fetch_res_data)
    def test_search_page_session(self):
        session = self.client.session
        session["last_query"] = {
            "query": "NY",
            "max_price": 2000,
            "min_price": 500,
            "bed_num": 4,
        }
        session.save()

        response = self.client.get("/search/")
        self.assertContains(response, "Address:")
        self.assertContains(response, "Max Price: 2000")
        self.assertContains(response, "Min Price: 500")
        self.assertContains(response, "Number of Bedroom: 4")


@mock.patch("external.res.fetch.fetch_res_data", fetch_res_data)
class DataResViewTests(TestCase):
    def test_data_res_page(self):
        response = self.client.get(reverse("data_res"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Restraunts Data Query")

    def test_data_res_form_submit(self):
        post_data = {"zipcode": "10003"}

        response = self.client.post(reverse("data_res"), post_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Restraunts Data Results")


class CustomTemplatesTestCases(TestCase):
    def test_get_item(self):
        tmp_dict = {"city": "Brooklyn"}
        result = get_item(tmp_dict, "city")
        self.assertEqual(result, "Brooklyn")

    def test_get_modulo(self):
        value = 5
        key = 3
        result = get_modulo(value, key)
        self.assertEqual(result, 2)


class SearchQueryBuilderTests(TestCase):
    def test_build_query_zip_only(self):
        """
        Tests the return value of the search query when
        the original zip code is the exact query
        """
        addr_dict = {
            "street": "",
            "zipcode": "11204",
            "city": "Brooklyn",
            "state": "NY",
            "latitude": 40.6195067,
            "longitude": -73.9859414,
            "locality": "Brooklyn",
        }
        addr = Address.from_dict(addr_dict)

        q_loc, q_apa = build_search_query(
            address=addr, orig_query="11204", min_price="", max_price="", bed_num=""
        )
        result_query_dict = {"zipcode": "11204"}
        self.assertDictEqual(q_loc, result_query_dict)

    def test_build_query_locality(self):
        """
        Tests the return value of build_search_query when
        the address locality is in the original query
        """
        addr_dict = {
            "street": "",
            "zipcode": "",
            "city": "Brooklyn",
            "state": "NY",
            "latitude": 40.6195067,
            "longitude": -73.9859414,
            "locality": "Brooklyn",
        }
        addr = Address.from_dict(addr_dict)

        q_loc, q_apa = build_search_query(
            address=addr,
            orig_query="Brooklyn, NY",
            min_price="",
            max_price="",
            bed_num="",
        )
        result_query_dict = {
            "locality__iexact": "Brooklyn",
            "state__iexact": "NY",
            "apartment_set__is_rented": False,
        }
        self.assertDictEqual(q_loc, result_query_dict)
