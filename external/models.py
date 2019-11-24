import attr
from django.db import models


class CachedSearch(models.Model):
    """
    while an in memory cache would probably be more performant
    we want something that will persist over time so we can keep
    our usage of the Geocode API down
    """

    # we set db_index=True here since we will be exclusively searching on this table
    # against this field, and we want to make those searches as fast as possible.
    search_string = models.CharField(max_length=255, db_index=True)
    street = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )


@attr.s
class Address(object):
    street = attr.ib()
    zipcode = attr.ib(converter=str)
    city = attr.ib()
    state = attr.ib()
    latitude = attr.ib(converter=float)
    longitude = attr.ib(converter=float)

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)

    @property
    def full_address(self):
        components = [self.street, self.city, self.state, self.zipcode]
        return ", ".join(filter(lambda x: x, components))
