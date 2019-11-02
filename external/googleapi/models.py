import attr
from typing import List


@attr.s
class GeocodeAddressComponent(object):
    long_name = attr.ib()
    short_name = attr.ib()
    types: List[str] = attr.ib()


@attr.s
class GeocodeLocation(object):
    lat = attr.ib(converter=float)
    lng = attr.ib(converter=float)


@attr.s
class GeocodeViewport(object):
    northeast: GeocodeLocation = attr.ib()
    southwest: GeocodeLocation = attr.ib()


@attr.s
class GeocodeGeometry(object):
    location: GeocodeLocation = attr.ib()
    location_type = attr.ib()
    viewport: GeocodeViewport = attr.ib()


"""
@attr.s
class GeocodePostCodeLocalities(object):
    compound_code = attr.ib()
    global_code = attr.ib()
"""


@attr.s
class GeocodeResponse(object):
    address_components: List[GeocodeAddressComponent] = attr.ib()
    formatted_address = attr.ib()
    geometry: GeocodeGeometry = attr.ib()
    place_id = attr.ib()
    postcode_localities: List[str] = attr.ib()
    postal = attr.ib(converter=str)
    types: List[str] = attr.ib()
    # plus_code: List[str] = attr.ib()
