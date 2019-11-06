from django.db import models
from location.models import Location


class ZillowHousing(models.Model):
    zpid = models.CharField(max_length=255, primary_key=True)
    estimated_rent_price = models.DecimalField(max_digits=20, decimal_places=2)
    estimated_rent_price_currency = models.CharField(max_length=10)
    last_estimated = models.DateField()
    last_modified = models.DateTimeField(auto_now=True)
    url = models.URLField()
    suite_num = models.CharField(max_length=30, blank=True, null=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="zillow_set"
    )

    def __str__(self):
        return f"ZillowHousing({self.zpid}, {self.url}) - {self.location.address}"

    @property
    def estimated_rent_price_for_display(self):
        return f"{self.estimated_rent_price_currency} {self.estimated_rent_price}"
