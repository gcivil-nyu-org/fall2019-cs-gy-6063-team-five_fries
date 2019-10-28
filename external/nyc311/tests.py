from django.test import TestCase
from .get_311_statistics import get_311_statistics
from unittest import mock
from .stub import fetch_311_data
from .models import NYC311Statistics


@mock.patch("external.nyc311.get_311_data.fetch_311_data", fetch_311_data)
class NYC311StatiscticsTests(TestCase):
    def test_statistics_returns(self):
        try:
            stats = get_311_statistics("11201")
            for s in stats:
                self.assertTrue(isinstance(s, NYC311Statistics))
        except TimeoutError:
            pass

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
