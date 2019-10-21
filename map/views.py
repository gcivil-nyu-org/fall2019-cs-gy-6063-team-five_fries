from django.shortcuts import render
from search.models import CraigslistLocation
from map.models import CityStreetSpot

def mapview(request):
    craigslist_datas = CraigslistLocation.objects.all()
    marker = CityStreetSpot
    for data in craigslist_datas:
        if not CityStreetSpot.objects.filter(c_id = data.c_id).exists():
            marker = CityStreetSpot()
            title = data.name
            description = data.price + "\n" + str(data.date_time) + "\n" + data.url

            # TODO: fetch img from data.url
            image_url = "no_apa_pic.png"

            geom = dict({'type': 'Point', 'coordinates': [data.lon, data.lat]})

            q = CityStreetSpot(
                c_id = data.c_id,
                title = title,
                description = description,
                picture = image_url,
                geom = geom
            )
            q.save()
        # TODO: UPDATE data, if exist but had updating crag data

    return render(request, "map.html")
