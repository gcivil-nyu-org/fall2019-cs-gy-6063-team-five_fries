from django.shortcuts import render
from search.models import CraigslistLocation
from map.models import CityStreetSpot


def mapview(request):
    craigslist_datas = CraigslistLocation.objects.all()
    citystreet_obj = CityStreetSpot.objects

    for data in craigslist_datas:
        if not citystreet_obj.filter(c_id=data.c_id).exists():
            title = data.name
            url = "<a href=\"" +  data.url + "\">" +  data.url + "</a>"
            description = data.price + "\n" + str(data.date_time) + "\n" + url

            # TODO: fetch img from data.url
            image_url = "no_apa_pic.jpg"

            geom = dict({"type": "Point", "coordinates": [data.lon, data.lat]})

            q = CityStreetSpot(
                c_id=data.c_id,
                title=title,
                description=description,
                last_update=data.date_time,
                picture=image_url,
                geom=geom,
            )
            q.save()
        elif data.date_time != citystreet_obj.get(c_id=data.c_id).last_update:
            title = data.name
            url = "<a href=\"" + data.url + "\">" + data.url + "</a>"
            description = data.price + "\n" + str(data.date_time) + "\n" + url

            # TODO: fetch img from data.url
            image_url = "no_apa_pic.jpg"

            geom = dict({"type": "Point", "coordinates": [data.lon, data.lat]})

            citystreet_obj.filter(c_id=data.c_id).update(
                title=title,
                description=description,
                last_update=data.date_time,
                picture=image_url,
                geom=geom,
            )

    return render(request, "map.html")
