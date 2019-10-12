# from django.db import models

# Create your models here.

class CraigslistLocation(models.Model):
    c_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    date_time = models.DateTimeField()
    url = models.URLField()
    where = models.CharField(max_length=200)
    has_image = models.BooleanField(default=False)
    has_map = models.BooleanField(default=False)
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    lon = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)