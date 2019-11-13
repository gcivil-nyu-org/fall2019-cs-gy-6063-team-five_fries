import attr
import decimal
from datetime import datetime
from attr.converters import optional


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

    @property
    def full_address(self):
        return f"{self.street}, {self.city}, {self.state}, {self.zipcode}"


@attr.s
class ZillowHousingResponse(object):
    zpid = attr.ib()
    address = attr.ib(converter=optional(ZillowAddress.from_dict))
    estimated_rent_price = attr.ib(converter=optional(decimal.Decimal))
    estimated_rent_price_currency = attr.ib()
    last_estimated = attr.ib(converter=optional(parse_zillow_datetime))
    url = attr.ib()

    @classmethod
    def from_zillow_response(cls, dic):
        try:
            rent_estimate = dic["rentzestimate"]["amount"]
        except KeyError:
            rent_estimate = {}

        return cls(
            zpid=dic.get("zpid"),
            address=dic.get("address"),
            estimated_rent_price=rent_estimate.get("#text"),
            estimated_rent_price_currency=rent_estimate.get("@currency"),
            last_estimated=dic.get("rentzestimate", {}).get("last-updated"),
            url=dic.get("links", {}).get("mapthishome"),
        )

    @property
    def estimated_rent_price_for_display(self):
        return f"{self.estimated_rent_price_currency} {self.estimated_rent_price}"
