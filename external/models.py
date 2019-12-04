import attr
from django.db import models
from django.core.exceptions import ValidationError
from localflavor.us import models as us_models


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
    locality = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )

    def save(self, **kwargs):
        if (self.latitude and self.longitude is None) or (
            self.latitude is None and self.longitude
        ):
            print(f"Validation error on: {self.search_string}")
            raise ValidationError(
                "Either both latitude and longitude must have values or both must be null"
            )
        super().save(**kwargs)


@attr.s
class Address(object):
    street = attr.ib()
    zipcode = attr.ib(converter=str)
    city = attr.ib()
    state = attr.ib()
    latitude = attr.ib(converter=float)
    longitude = attr.ib(converter=float)
    locality = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(str)),
    )

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)

    @property
    def full_address(self):
        components = [self.street, self.city, self.state, self.zipcode]
        return ", ".join(filter(lambda x: x, components))


class NYC311Statistics(models.Model):
    zipcode = us_models.USZipCodeField(db_index=True)

    complaint_type = models.CharField(max_length=255)
    complaint_level = models.IntegerField()
    total_complaints_query_zip = models.IntegerField()
    closed_complaints_query_zip = models.IntegerField()
    percentage_complaints_closed = models.FloatField()
    max_complaints = models.IntegerField()
    max_complaints_zip = us_models.USZipCodeField()

    last_updated = models.DateTimeField(auto_now=True)

    @classmethod
    def from_statistics(cls, zipcode, stat):
        return cls(
            zipcode=zipcode,
            complaint_type=stat.complaint_type,
            complaint_level=stat.complaint_level,
            total_complaints_query_zip=stat.total_complaints_query_zip,
            closed_complaints_query_zip=stat.closed_complaints_query_zip,
            percentage_complaints_closed=stat.percentage_complaints_closed,
            max_complaints=stat.max_complaints,
            max_complaints_zip=stat.max_complaints_zip,
        )
