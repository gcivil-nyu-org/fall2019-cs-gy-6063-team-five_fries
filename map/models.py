# from django.db import models
# from djgeojson.fields import PointField

# # from search.models import CraigslistLocation
# from location.models import Apartment


# class CityStreetSpot(models.Model):

#     #c_id = models.ForeignKey(CraigslistLocation, on_delete=models.CASCADE)
#     c_id = models.ForeignKey(Apartment, on_delete=models.CASCADE)
#     title = models.CharField(max_length=256)
#     description = models.TextField()
#     last_update = models.DateTimeField()
#     picture = models.ImageField(upload_to="./map/static/map")
#     geom = PointField()

#     def __unicode__(self):
#         return self.title

#     @property
#     def picture_url(self):
#         return "/static/map/" + self.picture.url
