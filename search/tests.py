from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

import datetime
from .models import CraigslistLocation, LastRetrievedData


# Create your tests here.


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


class SearchIndexViewTests(TestCase):
    def test_search_index(self):
        """
        Tests the index page, insuring the navigational buttons
        are rendered
        """
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Get Zillow Listings")
        self.assertContains(response, "Get Craigslist Listings")


class SearchCraigsTests(TestCase):
    def test_search_clist_results(self):
        """
        Tests the craigslist result page
        """
        pass
        # TODO: uncomment it after we mock the craigslist API
        # response = self.client.get(reverse("clist_results"))
        # self.assertEqual(response.status_code, 200)
