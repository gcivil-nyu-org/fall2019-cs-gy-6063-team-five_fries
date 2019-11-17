import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from external.craigslist import fetch_craigslist_housing
from external.googleapi.fetch import fetch_reverse_geocode
from location.models import Location
from location.models import Apartment

def autofetch(request):
    #city_list = ["brx", "brk", "fct", "lgi", "mnh", "jsy", "que", "stn", "wch"]
    city_list = ["brk"]

    for city_name in city_list:
        results = fetch_craigslist_housing(
            #limit=10,
            site="newyork",
            category="apa",
            area=city_name,
        )

        for r in results:
            # check if is_existed w/ address reversed from lat,lon
            lat, lon = None, None
            print(r)

            # reverse (lat, lon) to address
            if r["geotag"] is not None:
                lat = r["geotag"][0]
                lon = r["geotag"][1]
                reverse_response = fetch_reverse_geocode((lat, lon))
                full_address = reverse_response[0]["formatted_address"]

                # example of formatted_address: 570 4th Ave, Brooklyn, NY 11215, USA
                address = full_address.split(',')[0]
                city = full_address.split(',')[1].split(' ')[1]
                state = full_address.split(',')[2].split(' ')[1]
                zipcode = reverse_response[0]["postal"]

            else:
                continue

            loc, loc_created = Location.objects.get_or_create(
                address=address,
                city=city,
                state=state,
                zipcode=zipcode,
                latitude=lat,
                longitude=lon,
            )

            c_id = r["id"]
            url = r["url"]
            has_image = r["has_image"]
            price = int(r["price"].split("$")[1])
            last_updated = r["last_updated"]
            bedrooms = r["bedrooms"]

            apartment, apa_created = Apartment.objects.get_or_create(
                c_id=c_id,
                location=loc
            )

            if apa_created:
                apartment.rent_price = price
                apartment.number_of_bed = bedrooms
                apartment.last_modified = last_updated
                apartment.save()

    return render(request, "account.html")