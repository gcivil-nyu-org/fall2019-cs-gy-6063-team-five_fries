from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from unittest import mock

import datetime
from .models import CraigslistLocation, LastRetrievedData
from external.models import Address
from location.models import Location, Apartment
from external.craigslist.stub import fetch_craigslist_housing
from external.nyc311.stub import fetch_311_data
from external.googleapi.stub import fetch_geocode as fetch_geocode_stub
from external.res.stub import fetch_res_data
from .templatetags.custom_tags import get_item, get_modulo


def create_c_location(
    id,
    name="A cool place to live",
    url="http://a-url.com",
    days=0,
    price="$3.50",
    where="Sunnyside Heights",
    has_image=False,
    has_map=False,
    lat=40.772480,
    lon=-73.972580,
):
    """
    Creates a CraigslistLocation with the given values
    and datetime the given number of 'days' offset to now
    (negative for times in the past, positive for times in
    the future)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    # Used ternary so it's not necessary to fill in every field
    # each time a location is created.
    return CraigslistLocation.objects.create(
        c_id=id,
        name=name,
        url=url,
        date_time=time,
        price=price,
        where=where,
        has_image=has_image,
        has_map=has_map,
        lat=lat,
        lon=lon,
    )


def create_last_pulled(days, model):
    time = timezone.now() + datetime.timedelta(days=days)
    return LastRetrievedData.objects.create(time=time, model=model)


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


class LastRetrieveDataModelTests(TestCase):
    def test_str_method(self):
        """
        tests the __str__ method to insure it returns the correct value
        """
        q = create_last_pulled(days=0, model="TestModel")
        self.assertEqual(str(q), q.model)

    def test_future_date(self):
        """
        was_retrieved_recently() returns False for Retrieval
        whose time was in the future
        """
        time = timezone.now() + datetime.timedelta(days=1, seconds=1)
        future_retrieval = LastRetrievedData(time=time)
        self.assertIs(future_retrieval.should_retrieve(), False)

    def test_with_current(self):
        """
        was_retrieved_recently() should return False for Retrievals
        within the past day
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        old_retrieval = LastRetrievedData(time=time)
        self.assertIs(old_retrieval.should_retrieve(), False)

    def test_with_past(self):
        """
        was_retrieved_recently() should return True for Retrievals
        older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_retrieval = LastRetrievedData(time=time)
        self.assertIs(old_retrieval.should_retrieve(), True)


class CraigslistLocationTests(TestCase):
    def test_loc_name(self):
        """
        tests the name of a craigslistLocation to insure that the __self__
        method is returning correctly
        """
        q = create_c_location(id="123", name="Test_Loc")
        self.assertEqual(str(q), "123 - Test_Loc")


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

    @mock.patch("search.views.fetch_craigslist_housing", fetch_craigslist_housing)
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

    @mock.patch("search.views.fetch_craigslist_housing", fetch_craigslist_housing)
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

    @mock.patch("search.views.fetch_craigslist_housing", fetch_craigslist_housing)
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

    @mock.patch("search.views.fetch_craigslist_housing", fetch_craigslist_housing)
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

    @mock.patch("search.views.fetch_craigslist_housing", fetch_craigslist_housing)
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

    @mock.patch("search.views.fetch_craigslist_housing", fetch_craigslist_housing)
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

    @mock.patch("search.views.fetch_craigslist_housing", fetch_craigslist_housing)
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
        # response = self.client.get(
        #     "/search/?query=NY&min_price=500&max_price=2000&bed_num=4"
        # )
        response = self.client.get("/search/")
        self.assertContains(response, "Address:")
        self.assertContains(response, "Max Price: 2000")
        self.assertContains(response, "Min Price: 500")
        self.assertContains(response, "Number of Bedroom: 4")


class SearchCraigsTests(TestCase):
    @mock.patch("search.views.fetch_craigslist_housing", fetch_craigslist_housing)
    def test_search_clist_results(self):
        """
        Tests the craigslist result page
        """
        pass
        response = self.client.get(reverse("clist_results"))
        self.assertEqual(response.status_code, 200)


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
