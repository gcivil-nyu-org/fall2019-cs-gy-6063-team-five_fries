from django.db import models

from mainapp.models import SiteUser
from location.models import Location


class Review(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)

    content = models.TextField()
    time = models.DateTimeField()

    def __str__(self):
        return "%s: %s" % (self.user, self.content)
