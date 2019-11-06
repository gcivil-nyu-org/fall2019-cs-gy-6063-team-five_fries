from django.db import models

from mainapp.models import SiteUser
from location.models import Location
from django.core.validators import MaxValueValidator, MinValueValidator


class Review(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)

    content = models.TextField()
    rating = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=False,
        null=False,
    )
    time = models.DateTimeField()

    def __str__(self):
        return "%s: %s" % (self.user, self.content)
