import attr
from typing import List


@attr.s
class GeocodeAddressComponent(object):

    long_name = attr.ib()
    short_name = attr.ib()
    types: List[str] = attr.ib(factory=list)

    @classmethod
    def list_converter(cls, list):
        return [GeocodeAddressComponent.from_any(li) for li in list]

    @classmethod
    def from_any(cls, ob):
        if isinstance(ob, GeocodeAddressComponent):
            return cls.from_obj(ob)
        else:
            return cls.from_dict(ob)

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)

    @classmethod
    def from_obj(cls, obj):
        return cls(long_name=obj.long_name, short_name=obj.short_name, types=obj.types)


@attr.s
class GeocodeLocation(object):
    lat = attr.ib(converter=float)
    lng = attr.ib(converter=float)

    @classmethod
    def from_any(cls, ob):
        if isinstance(ob, GeocodeLocation):
            return cls.from_obj(ob)
        else:
            return cls.from_dict(ob)

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)

    @classmethod
    def from_obj(cls, obj):
        return cls(lat=obj.lat, lng=obj.lng)


@attr.s
class GeocodeViewport(object):
    northeast: GeocodeLocation = attr.ib(converter=GeocodeLocation.from_any)
    southwest: GeocodeLocation = attr.ib(converter=GeocodeLocation.from_any)

    @classmethod
    def from_any(cls, ob):
        if isinstance(ob, GeocodeViewport):
            return cls.from_obj(ob)
        else:
            return cls.from_dict(ob)

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)

    @classmethod
    def from_obj(cls, obj):
        return cls(northeast=obj.northeast, southwest=obj.southwest)


@attr.s
class GeocodeGeometry(object):
    bounds: GeocodeViewport = attr.ib(converter=GeocodeViewport.from_any)
    location: GeocodeLocation = attr.ib(converter=GeocodeLocation.from_any)
    location_type = attr.ib()
    viewport: GeocodeViewport = attr.ib(converter=GeocodeViewport.from_any)

    @classmethod
    def from_any(cls, ob):
        if isinstance(ob, GeocodeGeometry):
            return cls.from_obj(ob)
        else:
            return cls.from_dict(ob)

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)

    @classmethod
    def from_obj(cls, obj):
        return cls(
            bounds=obj.bounds,
            location=obj.location,
            location_type=obj.location_type,
            viewport=obj.viewport,
        )


@attr.s
class GeocodeResponse(object):
    formatted_address = attr.ib()
    place_id = attr.ib()
    postal = attr.ib(converter=str)
    geometry: GeocodeGeometry = attr.ib(converter=GeocodeGeometry.from_any)
    postcode_localities: List[str] = attr.ib(factory=list)
    types: List[str] = attr.ib(factory=list)
    address_components: List[GeocodeAddressComponent] = attr.ib(
        converter=GeocodeAddressComponent.list_converter, factory=list
    )

    @classmethod
    def from_any(cls, ob):
        if isinstance(ob, GeocodeResponse):
            return cls.from_obj(ob)
        else:
            return cls.from_dict(ob)

    @classmethod
    def from_dict(cls, dict):
        return cls(**dict)

    @classmethod
    def from_obj(cls, obj):
        return cls(
            address_components=obj.address_components,
            formatted_address=obj.formatted_address,
            geometry=obj.geometry,
            place_id=obj.place_id,
            postcode_localities=obj.postcode_localities,
            postal=obj.postal,
            types=obj.types,
        )
