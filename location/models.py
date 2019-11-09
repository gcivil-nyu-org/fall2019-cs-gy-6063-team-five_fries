from django.db import models
from localflavor.us import models as us_models
from urllib.parse import quote
from django.core.validators import MinValueValidator


class Location(models.Model):
    city = models.CharField(max_length=100)
    state = us_models.USStateField()
    address = models.CharField(max_length=255)
    zipcode = us_models.USZipCodeField()
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    last_fetched_zillow = models.DateTimeField(blank=True, null=True)

    @property
    def full_address(self):
        addr_components = map(str, [self.address, self.city, self.state, self.zipcode])
        return ", ".join(addr_components)

    @property
    def url_encoded_full_address(self):
        return quote(self.full_address)

    @property
    def google_map_url(self):
        return f"https://www.google.com/maps/search/?api=1&query={self.url_encoded_full_address}"


class Apartment(models.Model):
    suite_num = models.CharField(max_length=30, blank=True, null=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="apartment_set"
    )

    rent_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, validators=[MinValueValidator(0)]
    )
    number_of_bed = models.IntegerField(null=True, validators=[MinValueValidator(0)])

    # Zillow
    zpid = models.CharField(max_length=255, unique=True)
    estimated_rent_price = models.DecimalField(max_digits=20, decimal_places=2)
    estimated_rent_price_currency = models.CharField(max_length=10)
    last_estimated = models.DateField()
    last_modified = models.DateTimeField(auto_now=True)
    zillow_url = models.URLField()

    def __str__(self):
        return f"Apartment({self.suite_num}) - {self.location.address}"

    @property
    def estimated_rent_price_for_display(self):
        return f"{self.estimated_rent_price_currency} {self.estimated_rent_price}"
