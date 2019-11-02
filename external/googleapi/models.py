import attr
from typing import List


@attr.s
class GeocodeAddressComponent(object):
    long_name = attr.ib()
    short_name = attr.ib()
    types: List[str] = attr.ib(factory=list)

    @classmethod
    def get_converter(cls, ob):
        if isinstance(ob, GeocodeAddressComponent):
            return cls.from_obj
        else:
            return cls.from_dict

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
    def get_converter(cls, ob):
        if isinstance(ob, GeocodeLocation):
            return cls.from_obj
        else:
            return cls.from_dict

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)

    @classmethod
    def from_obj(cls, obj):
        return cls(lat=obj.lat, lng=obj.lng)


@attr.s
class GeocodeViewport(object):
    northeast: GeocodeLocation = attr.ib(converter=GeocodeLocation.get_converter)
    southwest: GeocodeLocation = attr.ib(converter=GeocodeLocation.get_converter)

    @classmethod
    def get_converter(cls, ob):
        if isinstance(ob, GeocodeViewport):
            return cls.from_obj
        else:
            return cls.from_dict

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)

    @classmethod
    def from_obj(cls, obj):
        return cls(northeast=obj.northeast, southwest=obj.southwest)


@attr.s
class GeocodeGeometry(object):
    # bounds: GeocodeViewport = attr.ib(converter=GeocodeViewport.get_converter)
    location: GeocodeLocation = attr.ib(converter=GeocodeLocation.get_converter)
    location_type = attr.ib()
    viewport: GeocodeViewport = attr.ib(converter=GeocodeViewport.get_converter)

    @classmethod
    def get_converter(cls, ob):
        if isinstance(ob, GeocodeGeometry):
            return cls.from_obj
        else:
            return cls.from_dict

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)

    @classmethod
    def from_obj(cls, obj):
        return cls(
            # bounds=obj.bounds,
            location=obj.location,
            location_type=obj.location_type,
            viewport=obj.viewport,
        )


@attr.s
class GeocodeResponse(object):
    formatted_address = attr.ib()
    place_id = attr.ib()
    postal = attr.ib(converter=str)
    geometry: GeocodeGeometry = attr.ib(converter=GeocodeGeometry.get_converter)
    postcode_localities: List[str] = attr.ib(factory=list)
    types: List[str] = attr.ib(factory=List)
    address_components: List[GeocodeAddressComponent] = attr.ib(factory=list)
    # plus_code: List[str] = attr.ib()

    @classmethod
    def get_converter(cls, ob):
        if isinstance(ob, GeocodeResponse):
            return cls.from_obj
        else:
            return cls.from_dict

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
