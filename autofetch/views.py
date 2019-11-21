from django.shortcuts import render
from external.craigslist import fetch_craigslist_housing
from external.googleapi.fetch import fetch_reverse_geocode
from location.models import Location
from location.models import Apartment
from datetime import datetime
from celery import shared_task
from external.googleapi.g_utils import normalize_us_address
import googlemaps


def autofetch(request):
    CITY_LIST = ["brx", "brk", "fct", "lgi", "mnh", "jsy", "que", "stn", "wch"]
    # The huge query: /autofetch/?city=brx,brk,fct,lgi,mnh,jsy,que,stn,wch&limit=1000000
    if request.method == "GET":
        # allow get param in url /autofetch/?city=brk,brx&limit=100
        city_list, city, limit = set(), list(), 100
        if "city" in request.GET:
            city = request.GET.get("city").split(',')
        if "limit" in request.GET:
            limit = request.GET.get("limit")
        for c in city:
            if c in CITY_LIST:
                city_list.add(c)
        bckgrndfetch.delay(list(city_list), int(limit))
    return render(request, "account.html")


@shared_task
def bckgrndfetch(city_list, limit):

    print(f"Start: {str(datetime.now())} \n")

    for city_name in city_list:
        try:
            results = fetch_craigslist_housing(
                limit=limit,
                site="newyork",
                category="apa",
                area=city_name,
            )
        except AttributeError:
            print(f" Cannot write into city: {city_name}, because one of the url not exist\n")

            continue

        for r in results:
            # check if is_existed w/ address reversed from lat,lon
            if r["geotag"] is not None:
                address, city, state, zipcode, full_address = "", "", "NY", 11201, ""
                lat = r["geotag"][0]
                lon = r["geotag"][1]
                try:
                    reverse_response = fetch_reverse_geocode((lat, lon))
                except googlemaps.exceptions.TransportError:
                    continue

                if "formatted_address" in reverse_response[0].keys():
                    full_address = reverse_response[0]["formatted_address"]

                normalize_addr_dic = normalize_us_address(full_address)

                if not normalize_addr_dic:
                    continue

                state = normalize_addr_dic.state
                address = normalize_addr_dic.street
                city = normalize_addr_dic.city
                zipcode = normalize_addr_dic.zipcode

            else:
                continue

            # match the not null constraint of postgre
            if state is None or address is None or city is None or zipcode is None:
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
                location=loc,
            )

            if apa_created:
                apartment.rent_price = price
                apartment.number_of_bed = bedrooms
                apartment.last_modified = last_updated
                apartment.save()
            elif apartment.last_modified != last_updated:
                apartment.rent_price = price
                apartment.number_of_bed = bedrooms
                apartment.last_modified = last_updated
                apartment.save()

        print(" Finish query\n")

    print(f"End at: {str(datetime.now())} \n")