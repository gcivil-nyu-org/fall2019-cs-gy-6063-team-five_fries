from django.test import TestCase
from django.utils import timezone 

import datetime
from .models import CraigslistLocation


# Create your tests here.


def create_c_location(id, name, url, date_time, days, price, where, 
    has_image, has_map, lat, lon):
    '''
    Creates a CraigslistLocation with the given values
    and datetime the given number of 'days' offset to now
    (negative for times in the past, positive for times in
    the future)
    '''
    timediff = 0 if (days is None) else days
    time = timezone.now() + datetime.timedelta(days=timediff)
    # Used ternary so it's not necessary to fill in every field
    # each time a location is created.
    return CraigslistLocation.objects.create(
        c_id=('1234' if (id is None) else id),
        name=('A cool place to live!' if (name is None) else name),
        url=('http://a-url.com' if (url is None) else url),
        date_time=time,
        price=('$3.50' if (price is None) else price),
        where=('Sunnyside Heights' if (where is None) else where),
        has_image=(False if (has_image is None) else has_image),
        has_map=(False if (has_map is None) else has_map),
        # coordinates for some random spot in Central Park
        lat=(40.772480 if (lat is None) else lat),
        lon=(-73.972580 if (lon is None) else lon)
    )

