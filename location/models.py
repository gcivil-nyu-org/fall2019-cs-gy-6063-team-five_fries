from django.db import models
from localflavor.us import models as us_models
from urllib.parse import quote


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
    def url_encoded_full_address(self):
        addr_components = map(str, [self.address, self.city, self.state, self.zipcode])
        return quote(", ".join(addr_components))

    @property
    def google_map_url(self):
        return f"https://www.google.com/maps/search/?api=1&query={self.url_encoded_full_address}"
