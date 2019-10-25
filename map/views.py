from django.shortcuts import render
from search.models import CraigslistLocation
from map.models import CityStreetSpot


def mapview(request):
    craigslist_datas = CraigslistLocation.objects.all()

    for data in craigslist_datas:
        title = data.name
        url = '<a href="' + data.url + '" target="_blank">' + data.url + "</a>"
        description = data.price + "\n" + str(data.date_time) + "\n" + url

        # TODO: fetch img from data.url
        image_url = "no_apa_pic.jpg"

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

    return render(request, "map.html")
