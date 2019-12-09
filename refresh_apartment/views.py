from bs4 import BeautifulSoup
import requests
from django.shortcuts import render
from external.craigslist import fetch_craigslist_housing
from external.googleapi.fetch import fetch_reverse_geocode
from location.models import Location, OtherImages
from location.models import Apartment
from datetime import datetime
from celery import shared_task
from external.googleapi.g_utils import normalize_us_address
import googlemaps


CITY_LIST = ["brx", "brk", "fct", "lgi", "mnh", "jsy", "que", "stn", "wch"]
DEFAULT_IMG_URL = "/static/img/no_img.png"
DEFAULT_DESCRIPTION = "DEFAULT DESCRIPTION"


def autofetch(request):

    # The huge query: /refresh_apartment/?city=brx,brk,fct,lgi,mnh,jsy,que,stn,wch&limit=1000000
    if request.method == "GET":
        # allow get param in url /refresh_apartment/?city=brk,brx&limit=100

        city_list, city, limit = set(), list(), 100

        if "city" in request.GET:
            city = request.GET.get("city").split(",")

        if "limit" in request.GET:
            limit = request.GET.get("limit")

        for c in city:
            if c in CITY_LIST:
                city_list.add(c)

        city_list = sorted(
            city_list
        )  # sorted for pass the test by having foreseeable order

        bckgrndfetch.delay(list(city_list), int(limit))

    return render(request, "account.html")


@shared_task
def bckgrndfetch(city_list, limit):

    print(f"Start: {str(datetime.now())} \n")

    for city_name in city_list:

        print(f"Fetching {city_name}............")

        try:
            results = fetch_craigslist_housing(
                limit=limit, site="newyork", category="apa", area=city_name
            )

        except AttributeError:
            print(
                f" Cannot write into city: {city_name}, because one of the url not exist\n"
            )
            continue

        print(f"Finished Fetching {city_name}..........")
        print(f"Parsing Response array for {city_name}.............")
        for r in results:

            c_id = r["id"]
            price = int(r["price"].split("$")[1])
            last_updated = r["last_updated"]
            bedrooms = r["bedrooms"]

            other_images, image_url, description = (
                [],
                DEFAULT_IMG_URL,
                DEFAULT_DESCRIPTION,
            )
            try:
                other_images, image_url, description = get_img_url_and_description(
                    r["url"]
                )
            except requests.exceptions.ConnectionError:
                pass

            if len(Apartment.objects.filter(c_id=c_id)) > 0:

                apartment = Apartment.objects.get(c_id=c_id)
                if apartment.last_modified != last_updated:

                    print(
                        f"city_name={city_name}: Found existing apartment for c_id = {c_id}, updating."
                    )

                    apartment.image = image_url
                    apartment.description = description
                    for other_image in other_images:
                        photo = OtherImages(apartment=apartment, image=other_image)
                        photo.save()

                    apartment.rent_price = price
                    apartment.number_of_bed = bedrooms
                    apartment.last_modified = last_updated
                    apartment.save()

            # Apartment not exist, create a location for it
            else:
                print(
                    f"city={city_name}:c_id={c_id}: No Existing locations found, preparing to create new"
                )
                # check if is_existed w/ address reversed from lat,lon
                if r["geotag"] is not None:

                    address, city, state, zipcode, full_address = (
                        "",
                        "",
                        "NY",
                        11201,
                        "",
                    )

                    lat = r["geotag"][0]
                    lon = r["geotag"][1]

                    try:
                        reverse_response = fetch_reverse_geocode((lat, lon))

                    except googlemaps.exceptions.TransportError:
                        print(googlemaps.exceptions.TransportError)
                        continue

                    if "formatted_address" in reverse_response[0].keys():
                        full_address = reverse_response[0]["formatted_address"]

                    normalize_addr_dic = normalize_us_address(full_address)

                    if not normalize_addr_dic:
                        print(
                            f"city={city_name}:c_id={c_id}: return None from nomalize_us_address"
                        )
                        print(
                            f"city={city_name}:c_id={c_id}: The address input is: {full_address}"
                        )
                        continue

                    state = normalize_addr_dic.state
                    address = normalize_addr_dic.street
                    city = normalize_addr_dic.city
                    locality = normalize_addr_dic.locality
                    zipcode = normalize_addr_dic.zipcode

                else:
                    print(
                        f"city={city_name}:c_id={c_id}: No geotag in craiglist results"
                    )
                    continue

                # match the not null constraint of postgre
                if not state or not address or not city or not zipcode or not locality:
                    print(
                        f"city={city_name}:c_id={c_id}: state, address, city or zipcode is None"
                    )
                    continue

                loc, loc_created = Location.objects.get_or_create(
                    address=address,
                    city=city,
                    state=state,
                    zipcode=zipcode,
                    locality=locality,
                )

                if loc_created:
                    loc.latitude = lat
                    loc.longitude = lon
                    loc.save()

                apartment, apa_created = Apartment.objects.get_or_create(
                    c_id=c_id, location=loc
                )

                for other_image in other_images:
                    photo = OtherImages(apartment=apartment, image=other_image)
                    photo.save()

                apartment.rent_price = price
                apartment.image = image_url
                apartment.description = description
                apartment.number_of_bed = bedrooms
                apartment.last_modified = last_updated
                apartment.save()

        print(" Finish query\n")

    print(f"End at: {str(datetime.now())} \n")


def get_img_url_and_description(url):
    result = requests.get(url)
    if result.status_code == 200:
        soup = BeautifulSoup(result.content, "html.parser")
        img_tag = soup.find_all("a", {"class": "thumb"})
        other_images = []
        for other_image in img_tag[1:]:
            if other_image.get("href"):
                other_images.append(other_image.get("href"))

        body = soup.find("section", id="postingbody")
        body_text = (
            (getattr(e, "text", e) for e in body if not getattr(e, "attrs", None))
            if body is not None
            else ""
        )
        description = "".join(body_text).strip()

        if len(img_tag) == 0 and description == "":
            return [], DEFAULT_IMG_URL, DEFAULT_DESCRIPTION
        elif len(img_tag) == 0:
            return [], DEFAULT_IMG_URL, description
        elif description == "":
            return other_images, img_tag[0].get("href"), DEFAULT_DESCRIPTION
        else:
            return other_images, img_tag[0].get("href"), description
    else:
        return [], DEFAULT_IMG_URL, DEFAULT_DESCRIPTION
