import attr
import decimal
from datetime import datetime


def parse_zillow_datetime(value):
    return datetime.strptime(value, "%m/%d/%Y")


@attr.s
class ZillowAddress(object):
    street = attr.ib()
    zipcode = attr.ib(converter=str)
    city = attr.ib()
    state = attr.ib()
    latitude = attr.ib(converter=float)
    longitude = attr.ib(converter=float)

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)


@attr.s
class ZillowHousing(object):
    zpid = attr.ib()
    address = attr.ib(converter=ZillowAddress.from_dict)
    estimated_rent_price = attr.ib(converter=decimal.Decimal)
    estimated_rent_price_currency = attr.ib()
    last_estimated = attr.ib(converter=parse_zillow_datetime)
    url = attr.ib()

    @classmethod
    def from_zillow_response(cls, dic):
        try:
            rent_estimate = dic["rentzestimate"]["amount"]
        except KeyError:
            rent_estimate = {}

        return cls(
            zpid=dic["zpid"],
            address=dic["address"],
            estimated_rent_price=rent_estimate.get("#text"),
            estimated_rent_price_currency=rent_estimate.get("@currency"),
            last_estimated=dic["rentzestimate"]["last-updated"],
            url=dic["links"]["mapthishome"],
        )

    @property
    def estimated_rent_price_for_display(self):
        return f"{self.estimated_rent_price_currency} {self.estimated_rent_price}"
