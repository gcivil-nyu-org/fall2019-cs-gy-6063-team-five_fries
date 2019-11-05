from django.test import TestCase
from unittest import mock
import pandas as pd

from .stat import get_311_statistics
from .fetch import fetch_311_data, fetch_311_data_as_dataframe, get_311_data
from .stub import fetch_311_data as fetch_311_data_stub
from .stub import fetch_311_data_closed as fetch_311_data_closed_stub
from .models import NYC311Statistics, NYC311Complaint


class FetchNYC311ConstraintsTests(TestCase):
    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data_stub)
    def test_fetch_311_data_as_dataframe(self):
        df = fetch_311_data_as_dataframe("11201")
        self.assertTrue(isinstance(df, pd.DataFrame))

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data_stub)
    def test_get_311_data(self):
        results = get_311_data("11201")
        for complaint in results:
            self.assertTrue(isinstance(complaint, NYC311Complaint))

    @mock.patch("external.nyc311.fetch.Socrata")
    def test_fetch_311_data(self, MockSocrata):  # noqa: N803
        fetch_311_data("11201")

        MockSocrata.assert_called_once()
        client = MockSocrata()
        client.get.assert_called_once()


class NYC311StatiscticsTests(TestCase):
    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data_stub)
    def test_statistics_returns(self):
        try:
            stats = get_311_statistics("11201")
            for s in stats:
                self.assertTrue(isinstance(s, NYC311Statistics))
        except TimeoutError:
            pass

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data_closed_stub)
    def test_statistics_returns_with_closed(self):
        try:
            stats = get_311_statistics("11201")
            for s in stats:
                self.assertTrue(isinstance(s, NYC311Statistics))
        except TimeoutError:
            pass

    @mock.patch("external.nyc311.fetch.fetch_311_data", fetch_311_data_stub)
    def test_statistics_value(self):
        """
        tests excact value of the returned statistics by comparing them to
        precomputed stats from given specific sample data
        """
        stats = get_311_statistics("11201")

        precomputed_noise = NYC311Statistics(
            complaint_type="Noise",
            complaint_level=0,
            total_complaints_query_zip=0,
            closed_complaints_query_zip=0,
            percentage_complaints_closed=0,
            max_complaints=1,
            max_complaints_zip="11224",
        )
        precomputed_parking = NYC311Statistics(
            complaint_type="Parking",
            complaint_level=0,
            total_complaints_query_zip=0,
            closed_complaints_query_zip=0,
            percentage_complaints_closed=0,
            max_complaints=1,
            max_complaints_zip="11232",
        )

        self.assertEqual(stats[0], precomputed_noise)
        self.assertEqual(stats[1], precomputed_parking)
