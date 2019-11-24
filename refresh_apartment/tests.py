import pytest
from django.test import TestCase
from unittest import mock
import os

# Create your tests here.


@pytest.mark.celery(CELERY_BROKER_URL=os.environ["REDIS_URL"])
@pytest.mark.celery(CELERY_RESULT_BACKEND=os.environ["REDIS_URL"])
class AutoFetchTests(TestCase):
    def test_autofetch_redirect(self):
        """
        Test the redirect functionality
        :return:
        """

        response = self.client.get("/refresh_apartment/?city=bk&limit=100")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account")

    @mock.patch("refresh_apartment.views.bckgrndfetch")
    def test_autofetch_valid_input(self, mockbckgrndfetch):  # noqa: N803
        """
        Tests the valid input for refresh_apartment/?city=<city,>&limit=<limit>/
        """

        response = self.client.get("/refresh_apartment/?city=brk,mnh&limit=100")
        self.assertEqual(response.status_code, 200)
        city_list = ["brk", "mnh"]
        mockbckgrndfetch.delay.assert_called_with(city_list, 100)

    @mock.patch("refresh_apartment.views.bckgrndfetch")
    def test_autofetch_invalid_input_without_limit(self, mockbckgrndfetch):
        """
        Tests the valid input for refresh_apartment/?city=<city,>&limit=<limit>/
        """
        response = self.client.get("/refresh_apartment/?city=brk,mnh")
        city_list = ["brk", "mnh"]
        self.assertEqual(response.status_code, 200)
        mockbckgrndfetch.delay.assert_called_with(city_list, 100)

    @mock.patch("refresh_apartment.views.bckgrndfetch")
    def test_autofetch_invalid_input_without_city(self, mockbckgrndfetch):
        """
        Tests the valid input for refresh_apartment/?city=<city,>&limit=<limit>/
        """
        response = self.client.get("/refresh_apartment/?limit=100")
        city_list = []
        self.assertEqual(response.status_code, 200)
        mockbckgrndfetch.delay.assert_called_with(city_list, 100)
