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

    def avg_rate(self):
        review_sum = 0
        for review in self.review_set.all():
            review_sum += review.rating
        if self.review_set.count() != 0:
            avg = review_sum / self.review_set.count()
            return float("%.2f" % round(avg, 2))
        else:
            return 0


class Apartment(models.Model):
    suite_num = models.CharField(unique=True, max_length=30, blank=True, null=True)
    image = models.ImageField(null = True, blank = True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="apartment_set"
    )

    rent_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, validators=[MinValueValidator(0)]
    )
    number_of_bed = models.IntegerField(null=True, validators=[MinValueValidator(0)])

    last_modified = models.DateTimeField(auto_now=True)

    # Zillow
    zpid = models.CharField(max_length=255, unique=True, blank=True, null=True)
    estimated_rent_price = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    last_estimated = models.DateField(blank=True, null=True)
    zillow_url = models.URLField(blank=True, null=True)
    is_zillow_listing = models.BooleanField(default=True)

    def __str__(self):
        return f"Apartment({self.suite_num}) - {self.location.address}"

    @property
    def estimated_rent_price_for_display(self):
        return f"${self.estimated_rent_price}"
