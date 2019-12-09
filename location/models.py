from django.db import models
from localflavor.us import models as us_models
from urllib.parse import quote
from django.core.validators import MinValueValidator, MaxValueValidator

import uuid


class Location(models.Model):
    city = models.CharField(max_length=100)
    # locality is for certain places (such as queens) where the google
    # locality and neighborhood are different
    locality = models.CharField(max_length=100, default="")
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

    @property
    def representative_image(self):
        return self.apartment_set.exclude(image=None).first().picture_url

    @property
    def representative_image_or_placeholder(self):
        image = self.representative_image
        return image if image is not None else "/static/img/no_img.png"

    @property
    def rent_price_for_display(self):
        count = self.apartment_set.count()
        if count == 0:
            return None
        elif count == 1:
            return self.apartment_set.first().rent_price_for_display
        else:
            minimum = f"{self.apartment_set.order_by('rent_price')[0].rent_price:.0f}"
            maximum = f"{self.apartment_set.order_by('-rent_price')[0].rent_price:.0f}"
            return f"${minimum} - {maximum}"

    def avg_rate(self):
        review_sum = 0
        for review in self.review_set.all():
            review_sum += review.rating
        if self.review_set.count() != 0:
            avg = review_sum / self.review_set.count()
            return float("%.2f" % round(avg, 2))
        else:
            return 0

    def check_tenant(self, user):
        return self.apartment_set.filter(tenant=user).exists()

    def check_landlord(self, user):
        return self.apartment_set.filter(landlord=user).exists()


class Apartment(models.Model):
    suite_num = models.CharField(max_length=30, blank=True, null=True)
    image = models.ImageField(null=True, blank=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="apartment_set"
    )
    rent_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(100000)],
    )
    number_of_bed = models.IntegerField(
        verbose_name="Bedrooms",
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    description = models.TextField(default="")
    last_modified = models.DateTimeField(auto_now=True)
    landlord = models.ForeignKey(
        "mainapp.SiteUser",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="landlord_apartment_set",
    )
    tenant = models.ForeignKey(
        "mainapp.SiteUser",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="tenant_apartment_set",
    )
    is_rented = models.BooleanField(
        verbose_name="Apartment has been rented?", default=False
    )

    # Craigslist
    c_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    # Zillow
    zpid = models.CharField(max_length=255, unique=True, blank=True, null=True)
    estimated_rent_price = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    last_estimated = models.DateField(blank=True, null=True)
    zillow_url = models.URLField(blank=True, null=True)

    class Meta:
        # enforces a uniqueness constraint on 'suite_num' and 'location' which
        # is handy for the update form
        unique_together = ("suite_num", "location")

    def __str__(self):
        return f"Apartment({self.suite_num}) - {self.location.address}"

    @property
    def rent_price_for_display(self):
        return f"${self.rent_price}"

    @property
    def picture_url(self):
        if not self.image:
            return None
        elif "http" not in self.image.url:
            return self.image.url
        else:
            return self.image


class OtherImages(models.Model):
    apartment = models.ForeignKey(Apartment, default=None, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, verbose_name="Image")

    @property
    def picture_url(self):
        if not self.image:
            return None
        elif "http" not in self.image.url:
            return self.image.url
        else:
            return self.image


class ClaimRequest(models.Model):
    user = models.ForeignKey("mainapp.SiteUser", null=True, on_delete=models.CASCADE)
    apartment = models.ForeignKey(
        Apartment, null=True, on_delete=models.CASCADE, related_name="claim_set"
    )
    request_type = models.CharField(
        max_length=100, choices=[("tenant", "Tenant"), ("landlord", "Landlord")]
    )
    note = models.TextField()
    access_granted = models.BooleanField(default=False)
    allow_token = models.UUIDField(default=uuid.uuid4, editable=False)
    deny_token = models.UUIDField(default=uuid.uuid4, editable=False)
