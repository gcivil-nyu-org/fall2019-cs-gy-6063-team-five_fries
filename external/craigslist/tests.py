from django.test import TestCase
from .fetch import fetch_craigslist_housing
from unittest import mock


class CraigslistTests(TestCase):
    @mock.patch("external.craigslist.fetch.CraigslistHousing")
    def test_fetch(self, MockCraigslistHousing):  # noqa: N803
        _ = fetch_craigslist_housing(
            limit=3,
            site="newyork",
            category="apa",
            area="brk",
            filters={"max_price": 2000},
        )
        MockCraigslistHousing.assert_called_with(
            site="newyork", category="apa", area="brk", filters={"max_price": 2000}
        )
        MockCraigslistHousing().get_results.assert_called_with(geotagged=True, limit=3)
