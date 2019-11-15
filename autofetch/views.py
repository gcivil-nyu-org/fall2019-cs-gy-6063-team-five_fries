from django.shortcuts import render
from external.craigslist import fetch_craigslist_housing
from external.googleapi.fetch import fetch_reverse_geocode
from location.models import Location

# TODO: parse address from class: mapaddress in craiglisturl, and normalize w/ google map api
def autofetch(request):
    #city_list = ["brx", "brk", "fct", "lgi", "mnh", "jsy", "que", "stn", "wch"]
    city_list = ["brk"]

    for city_name in city_list:
        results = fetch_craigslist_housing(
            limit=10,
            site="newyork",
            category="apa",
            area=city_name,
        )

        for r in results:
            # check if is_existed w/ address reversed from lat,lon
            lat = None
            lon = None

            # reverse (lat, lon) -> address
            if r["geotag"] is not None:
                lat = r["geotag"][0]
                lon = r["geotag"][1]
                reverse_response = fetch_reverse_geocode((lat, lon))
                address = reverse_response[0]["formatted_address"]
            else:
                continue

            loc, created = Location.objects.get_or_create(address=address)





