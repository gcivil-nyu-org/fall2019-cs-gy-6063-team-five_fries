import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from external.craigslist import fetch_craigslist_housing
from external.googleapi.fetch import fetch_reverse_geocode
from location.models import Location
from location.models import Apartment

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
            lat, lon = None, None
            print(r)

            # reverse (lat, lon) -> address
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

            apartment = Apartment.objects.get_or_create(
                #c_id=c_id,
                location=loc,
                rent_price=price,
                number_of_bed=bedrooms,
                last_modified=last_updated,
            )

    return render(request, "account.html")










# TODO: fetch img
# def get_img_url(url):
#     result = requests.get(url)
#     if result.status_code == 200:
#         soup = BeautifulSoup(result.content, "html.parser")
#         img_tag = soup.find_all("a", {"class": "thumb"})
#         # For now, get the first fullsize imgage.
#         # Get the image id by imgtag[n].get('data-imgid')
#         # Get the thumbnail image by imgtag[n].get('src')
#
#         if len(img_tag) == 0:
#             return "../static/map/no_apa_pic.jpg"
#         else:
#             return str(img_tag[0].get("href"))