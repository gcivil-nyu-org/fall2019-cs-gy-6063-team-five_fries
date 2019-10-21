from django.db import models
from djgeojson.fields import PointField


class CityStreetSpot(models.Model):

    c_id = models.CharField(max_length=200)
    title = models.CharField(max_length=256)
    description = models.TextField()
    picture = models.ImageField(upload_to="./map/static/map")
    geom = PointField()

    def __unicode__(self):
        return self.title

    @property
    def picture_url(self):
        return "/static/map/" + self.picture.url
