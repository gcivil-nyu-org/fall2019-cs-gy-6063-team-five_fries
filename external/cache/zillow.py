from ..models import ZillowHousing
from django.utils import timezone
import datetime
from external.zillow import get_zillow_housing


def refresh_zillow_housing(location):
    results = get_zillow_housing(
        address=location.address,
        city_state=f"{location.city}, {location.state}",
        zipcode=location.zipcode,
    )

    for response in results:
        if location.address != response.address.street:
            continue
        if location.city != response.address.city:
            continue

        ZillowHousing.objects.create(
            zpid=response.zpid,
            estimated_rent_price=response.estimated_rent_price,
            estimated_rent_price_currency=response.estimated_rent_price_currency,
            last_estimated=response.last_estimated,
            url=response.url,
            location=location,
        )


def refresh_zillow_housing_if_needed(location):
    if location.zillow_set.count() > 0:
        recent = location.zillow_set.latest("last_modified")
        now = timezone.now()
        if now - recent.last_modified < datetime.timedelta(days=1):
            return

    refresh_zillow_housing(location)
