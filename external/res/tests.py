from django.test import TestCase
from unittest import mock
import pandas as pd

from .fetch import fetch_res_data, fetch_res_data_as_dataframe, get_res_data
from .stub import fetch_res_data as fetch_res_data_stub
from .models import ResComplaint


class FetchResConstraintsTests(TestCase):
    @mock.patch("external.res.fetch.fetch_res_data", fetch_res_data_stub)
    def test_fetch_res_data_as_dataframe(self):
        df = fetch_res_data_as_dataframe("11201")
        self.assertTrue(isinstance(df, pd.DataFrame))

    @mock.patch("external.res.fetch.fetch_res_data", fetch_res_data_stub)
    def test_get_res_data(self):
        results = get_res_data("11201")
        for complaint in results:
            self.assertTrue(isinstance(complaint, ResComplaint))

    @mock.patch("external.res.fetch.Socrata")
    def test_fetch_res_data(self, MockSocrata):  # noqa: N803
        fetch_res_data("11201")
        MockSocrata.assert_called_once()
        client = MockSocrata()
        client.get.assert_called_once()
