from django.db import models
from djgeojson.fields import PointField

from search.models import CraigslistLocation


class CityStreetSpot(models.Model):

    c_id = models.OneToOneField(CraigslistLocation, on_delete=models.CASCADE, primary_key=True)
    title = models.CharField(max_length=256)
    description = models.TextField()
    last_update = models.DateTimeField()
    picture = models.ImageField()
    geom = PointField()

    def __unicode__(self):
        return self.title

    @property
    def picture_url(self):
        return self.picture.url
