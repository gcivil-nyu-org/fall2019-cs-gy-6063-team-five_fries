from django.shortcuts import render
import requests
from bs4 import BeautifulSoup

from search.models import CraigslistLocation
from map.models import CityStreetSpot


def mapview(request):
    craigslist_datas = CraigslistLocation.objects.all()

    for data in craigslist_datas:
        if not CityStreetSpot.objects.filter(c_id=data.c_id).exists():
            title = data.name
            url = '<a href="' + data.url + '" target="_blank">' + data.url + "</a>"
            description = data.price + "\n" + str(data.date_time) + "\n" + url

            image_url = "../static/map/no_apa_pic.jpg"
            if data.has_image:
                try:
                    image_url = get_img_url(data.url)
                except requests.exceptions.ConnectionError:
                    pass

            geom = dict({"type": "Point", "coordinates": [data.lon, data.lat]})

            q = CityStreetSpot(
                c_id=CraigslistLocation.objects.only("c_id").get(c_id=data.c_id),
                title=title,
                description=description,
                last_update=data.date_time,
                picture=image_url,
                geom=geom,
            )
            q.save()

        elif data.date_time != CityStreetSpot.objects.get(c_id=data.c_id).last_update:
            title = data.name
            url = '<a href="' + data.url + '" target="_blank">' + data.url + "</a>"
            description = data.price + "\n" + str(data.date_time) + "\n" + url

            image_url = "../static/map/no_apa_pic.jpg"
            if data.has_image:
                try:
                    image_url = get_img_url(data.url)
                except requests.exceptions.ConnectionError:
                    pass

            geom = dict({"type": "Point", "coordinates": [data.lon, data.lat]})

            CityStreetSpot.filter(c_id=data.c_id).update(
                title=title,
                description=description,
                last_update=data.date_time,
                picture=image_url,
                geom=geom,
            )
    return render(request, "map.html")


def get_img_url(url):
    result = requests.get(url)
    if result.status_code == 200:
        soup = BeautifulSoup(result.content, "html.parser")
        img_tag = soup.find_all("a", {"class": "thumb"})
        # For now, get the first fullsize imgage.
        # Get the image id by imgtag[n].get('data-imgid')
        # Get the thumbnail image by imgtag[n].get('src')
        # edit map.model to be more flexible //TODO: fix the image display for outer source

        if len(img_tag) == 0:
            return "../static/map/no_apa_pic.jpg"
        else:
            return str(img_tag[0].get("href"))
    else:
        return "../static/map/no_apa_pic.jpg"
