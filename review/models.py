from django.db import models

from mainapp.models import SiteUser
from location.models import Location


class Review(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        SiteUser, on_delete=models.CASCADE
    )

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    # TODO: MIGRATE THIS
    def __str__(self):
        return "%s: %s" % (self.user, self.content)