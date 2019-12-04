import pytest
from django.test import TestCase
from unittest import mock
from .stub import get_craigslist_response
from .views import get_img_url_and_description
import os

NORMAL_URL = "craigslist-url-normal.html"
NO_PIC_URL = "craigslist-url-no-pic.html"
NO_DESCRIPTION_URL = "craigslist-url-no-des.html"
NO_PIC_NO_DESCRIPTION_URL = "craigslist-url-no-pic-no-des.html"


class MockRequestResponse:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content


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

    @mock.patch(
        "refresh_apartment.views.requests"
    )  # all the requests in view is replaced with mock_requests here
    def test_normal_get_img_url_and_description(self, mock_requests):
        """
        :param mock_requests: mock the "requests" in your main code
        """
        # setup(mock) the object which requests.get(url) return
        craigslist_response_content = get_craigslist_response(NORMAL_URL)
        mock_resp_obj = MockRequestResponse(200, craigslist_response_content)

        # The moment that the mock take into place
        # When your test run the line "request.get" in your main code,
        # It would mock the obj that it return with `return_value`.
        mock_requests.get = mock.MagicMock(return_value=mock_resp_obj)

        url = (
            "./sample-response/craigslist-url-normal.html"
        )  # this url doesn't matter, could be whatever you like
        img_url, description = get_img_url_and_description(url)

        self.assertEqual(
            img_url, "https://images.craigslist.org/00H0H_2JxY7yF7CiN_600x450.jpg"
        )
        self.assertEqual(
            description,
            (
                "At the side of Crown Heights awaits an undiscovered jewel. "
                + "Located on Sterling Pl at Rochester Ave near the 3,4,A,C "
                + "trains in a beautiful, quiet pre-war building, this newly "
                + "renovated apartment is waiting for you!\n\n*New modern kitchen with stainless steel "
                + "appliances\n*Kitchen living room open concept\n*New gorgeous tiled bath\n*New "
                + "flooring throughout the apartment\n*Abundant sunlight through the large"
                + " windows\n*Great closet space\n*State of the art surveillance system\n*Very safe, "
                + "quiet & clean building \n*Heat and Hot water included \n*No pets\n\nGood credit and "
                + "income to qualify. Guarantors welcome.\nFor more information or to schedule a viewing "
                + "please call or text me at 201-297-6655",
            ),
        )

    @mock.patch("refresh_apartment.views.requests")
    def test_no_pic_get_img_url_and_description(self, mock_requests):
        """
        :param mock_requests: mock the "requests" in your main code
        """
        craigslist_response_content = get_craigslist_response(NO_PIC_URL)
        mock_resp_obj = MockRequestResponse(200, craigslist_response_content)

        mock_requests.get = mock.MagicMock(return_value=mock_resp_obj)

        url = "whatever.html"
        img_url, description = get_img_url_and_description(url)

        self.assertEqual(img_url, "/static/img/no_img.png")
        self.assertEqual(
            description,
            (
                "At the side of Crown Heights awaits an undiscovered jewel. "
                + "Located on Sterling Pl at Rochester Ave near the 3,4,A,C "
                + "trains in a beautiful, quiet pre-war building, this newly "
                + "renovated apartment is waiting for you!\n\n*New modern kitchen with stainless steel "
                + "appliances\n*Kitchen living room open concept\n*New gorgeous tiled bath\n*New "
                + "flooring throughout the apartment\n*Abundant sunlight through the large"
                + " windows\n*Great closet space\n*State of the art surveillance system\n*Very safe, "
                + "quiet & clean building \n*Heat and Hot water included \n*No pets\n\nGood credit and "
                + "income to qualify. Guarantors welcome.\nFor more information or to schedule a viewing "
                + "please call or text me at 201-297-6655",
            ),
        )

    @mock.patch("refresh_apartment.views.requests")
    def test_no_des_get_img_url_and_description(self, mock_requests):
        """
        :param mock_requests: mock the "requests" in your main code
        """
        craigslist_response_content = get_craigslist_response(NO_DESCRIPTION_URL)
        mock_resp_obj = MockRequestResponse(200, craigslist_response_content)

        mock_requests.get = mock.MagicMock(return_value=mock_resp_obj)

        url = "whatever.html"
        img_url, description = get_img_url_and_description(url)

        self.assertEqual(
            img_url, "https://images.craigslist.org/00H0H_2JxY7yF7CiN_600x450.jpg"
        )
        self.assertEqual(description, "DEFAULT DESCRIPTION")

    @mock.patch("refresh_apartment.views.requests")
    def test_no_pic_no_des_get_img_url_and_description(self, mock_requests):
        """
        :param mock_requests: mock the "requests" in your main code
        """
        craigslist_response_content = get_craigslist_response(NO_PIC_NO_DESCRIPTION_URL)
        mock_resp_obj = MockRequestResponse(200, craigslist_response_content)

        mock_requests.get = mock.MagicMock(return_value=mock_resp_obj)

        url = "whatever.html"
        img_url, description = get_img_url_and_description(url)

        self.assertEqual(img_url, "/static/img/no_img.png")
        self.assertEqual(description, "DEFAULT DESCRIPTION")
