import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from external.craigslist import fetch_craigslist_housing
from external.googleapi.fetch import fetch_reverse_geocode
from location.models import Location
from location.models import Apartment
from datetime import datetime

def autofetch(request):

    print(f"Start: {str(datetime.now())} \n")

    city_list = ["brx", "brk", "fct", "lgi", "mnh", "jsy", "que", "stn", "wch"]
    #city_list = ["brx", "brk"]

    for city_name in city_list:
        try:
            results = fetch_craigslist_housing(
                #limit=10,
                site="newyork",
                category="apa",
                area=city_name,
            )
        except AttributeError:
            print(f" Cannot write into city: {city_name}, because one of the url not exist\n")

            continue

        for r in results:
            # check if is_existed w/ address reversed from lat,lon
            lat, lon = None, None


            # reverse (lat, lon) to address
            if r["geotag"] is not None:
                address, city, state, zipcode, full_address = "", "", "NY", 11201, ""
                lat = r["geotag"][0]
                lon = r["geotag"][1]
                reverse_response = fetch_reverse_geocode((lat, lon))

                if "formatted_address" in reverse_response[0].keys():
                    full_address = reverse_response[0]["formatted_address"]

                # example of formatted_address: 570 4th Ave, Brooklyn, NY 11215, USA
                addr_len = len(full_address.split(','))

                if addr_len >= 1:
                    address = full_address.split(',')[0]
                if addr_len >= 2:
                    city = full_address.split(',')[1].split(' ')[1]
                if addr_len >= 3:
                    state = full_address.split(',')[2].split(' ')[1]
                if "postal" in reverse_response[0].keys():
                    zipcode = reverse_response[0]["postal"]

            else:
                continue

            loc, loc_created = Location.objects.get_or_create(
                address=address,
                city=city,
                state=state,
                zipcode=zipcode,
            )

            if loc_created:
                loc.latitude = lat
                loc.longitude = lon
                loc.save()

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
        print(" Finish query\n")

    print(f"End at: {str(datetime.now())} \n")

    return render(request, "account.html")