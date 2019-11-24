from django.utils import timezone
import datetime
from external.nyc311 import get_311_statistics
from ..models import NYC311Statistics


def refresh_nyc311_statistics(zipcode):
    results = get_311_statistics(zipcode)

    # remove the existing results
    NYC311Statistics.objects.filter(zipcode=zipcode).delete()

    NYC311Statistics.objects.bulk_create(
        NYC311Statistics.from_statistics(zipcode, stat) for stat in results
    )


def refresh_nyc311_statistics_if_needed(zipcode):
    stat = NYC311Statistics.objects.filter(zipcode=zipcode).first()

    now = timezone.now()
    if stat and now - stat.last_updated < datetime.timedelta(days=1):
        return

    refresh_nyc311_statistics(zipcode)
