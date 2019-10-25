from django.db import models
from django.utils import timezone
import datetime

# Create your models here.


class CraigslistLocation(models.Model):
    c_id = models.CharField(max_length=200, primary_key = True)
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    date_time = models.DateTimeField()
    url = models.URLField()
    price = models.CharField(max_length=200)
    where = models.CharField(max_length=200)
    has_image = models.BooleanField(default=False)
    has_map = models.BooleanField(default=False)
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    lon = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)

    def __str__(self):
        return f"{self.c_id} - {self.name}"


class LastRetrievedData(models.Model):
    model = models.CharField(max_length=200, unique=True)
    time = models.DateTimeField("last retrieval", default=datetime.datetime.now)

    def __str__(self):
        return self.model

    def should_retrieve(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) > self.time <= now
