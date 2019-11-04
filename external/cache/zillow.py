from ..models import ZillowHousing
from django.utils import timezone
import datetime
from external.zillow import get_zillow_housing
from streetaddress import StreetAddressParser


def refresh_zillow_housing(location):
    results = get_zillow_housing(
        address=location.address,
        city_state=f"{location.city}, {location.state}",
        zipcode=location.zipcode,
    )

    addr_parser = StreetAddressParser()
    for response in results:
        loc_addr = addr_parser.parse(location.full_address)
        response_addr = addr_parser.parse(response.address.full_address)
        if loc_addr["street_full"] != response_addr["street_full"]:
            continue
        if location.city != response.address.city:
            continue
        if location.state != response.address.state:
            continue

        ZillowHousing.objects.create(
            zpid=response.zpid,
            estimated_rent_price=response.estimated_rent_price,
            estimated_rent_price_currency=response.estimated_rent_price_currency,
            last_estimated=response.last_estimated,
            url=response.url,
            location=location,
        )
    location.last_fetched_zillow = timezone.now()
    location.save()


def refresh_zillow_housing_if_needed(location):
    if location.last_fetched_zillow:
        now = timezone.now()
        if now - location.last_fetched_zillow < datetime.timedelta(days=1):
            return

    refresh_zillow_housing(location)
