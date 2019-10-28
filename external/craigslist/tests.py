from django.test import TestCase
from .fetch import fetch_craigslist_housing
import numbers


class CraigslistTests(TestCase):
    def test_fetch(self):
        results = fetch_craigslist_housing(
            limit=3,
            site="newyork",
            category="apa",
            area="brk",
            filters={"max_price": 2000},
        )

        for r in results:
            if r["geotag"] is not None:
                self.assertTrue(len(r["geotag"]) >= 2)
                for p in r["geotag"]:
                    self.assertTrue(isinstance(p, numbers.Number))
            self.assertTrue("id" in r)
            self.assertTrue("name" in r)
            self.assertTrue("url" in r)
            self.assertTrue("datetime" in r)
            self.assertTrue("price" in r)
            self.assertTrue("has_image" in r)
