from typing import Optional, Dict, Tuple
from django.core.exceptions import ValidationError
from ..models import Address, CachedSearch
from .fetch import fetch_geocode


def parse_lat_lng(geo_result_obj):
    """
    Parses out a latitude/longitude tuple from the Google Geocoder response object
    """
    if geo_result_obj:
        if "geometry" in geo_result_obj.keys():
            geo = geo_result_obj["geometry"]
            if "location" in geo.keys():
                location = geo_result_obj["geometry"]["location"]
                return (location["lat"], location["lng"])

    # default case if there was no result returned
    return (None, None)


def normalize_us_address(address) -> Optional[Address]:
    if not address:
        return None

    # want to get rid of extraneous spaces and uppercase letters
    # as those don't matter to the Geocode API and will reduce the number
    # of extra Cache objects
    address = (" ".join(address.split())).lower()

    if CachedSearch.objects.filter(search_string=address).exists():
        cache = CachedSearch.objects.get(search_string=address)
        return Address(
            street=cache.street,
            city=cache.city,
            locality=cache.locality,
            state=cache.state,
            zipcode=cache.zipcode,
            latitude=cache.latitude,
            longitude=cache.longitude,
        )

    if (
        "ny" not in address.lower()
        or "new york" not in address.lower()
        or "newyork" not in address.lower()
    ):
        address += " ny"

    response_list = fetch_geocode(address, region="us")

    if not response_list:
        return None

    response = response_list[0]

    state = get_state(response)
    city, locality = get_city(response)
    street_num, route = get_address(response)
    zip_code = get_zipcode(response)
    lat, lon = get_location(response)

    if state != "NY":  # don't want to retrieve results not in NY
        print("Returned a result not in New York")
        print(
            f"Street: {street_num}, Route: {route}, city: {city}, locality: {locality}"
            f", state: {state}, zip: {zip_code}, lat: {lat}, lon: {lon}"
        )
        return None

    try:
        CachedSearch.objects.create(
            search_string=address,
            street=(" ".join(filter(lambda x: x, [street_num, route]))),
            city=(city if city is not None else ""),
            locality=(locality if locality is not None else ""),
            state=(state if state is not None else ""),
            zipcode=zip_code,
            latitude=lat,
            longitude=lon,
        )
    except ValidationError as e:
        print(f"ValidationError: {e}")
        print(f"Unable to cache search string: {address}, due to lat/lon error")

    return Address(
        street=" ".join(filter(lambda x: x, [street_num, route])),
        city=city,
        state=state,
        locality=locality,
        zipcode=zip_code,
        latitude=lat,
        longitude=lon,
    )


def get_address(g_result) -> Optional[Tuple[str, str]]:
    """
    Parses out the address component of a geocode result
    """
    result = get_result(g_result)

    route = ""
    street_num = ""
    for comp in result.get("address_components"):
        types = comp.get("types")

        if not types:
            continue

        if "route" in types:
            route = comp.get("long_name")

        if "street_number" in types:
            street_num = comp.get("long_name")

    return street_num, route


def get_state(g_result) -> Optional[str]:
    """
    Parses out the state component of a geocode result
    """
    result = get_result(g_result)

    state = None
    for comp in result.get("address_components"):
        types = comp.get("types")

        if not types:
            continue

        if "administrative_area_level_1" in types:
            state = comp.get("short_name")

    return state


def get_city(g_result) -> Optional[Tuple[str, str]]:
    """
    Parses out the city and locality components of a geocode result
    """
    result = get_result(g_result)

    locality = None
    city = None
    for comp in result.get("address_components"):
        types = comp.get("types")

        if not types:
            continue

        if "neighborhood" in types:
            city = comp.get("long_name")

        # https://stackoverflow.com/a/49640066/1556838
        if "locality" in types or "sublocality_level_1" in types:
            locality = comp.get("long_name")

    if not city:
        city = locality
    return city, locality


def get_zipcode(g_result) -> Optional[str]:
    """
    Parses out the zipcode component of a geocode result
    """
    result = get_result(g_result)
    zipcode = result.get("postal")

    if not zipcode:
        return ""
    else:
        return zipcode


def get_location(g_result) -> Optional[Tuple[any, any]]:
    """
    parses out the latitude/longitude component of a geocode result
    """
    result = get_result(g_result)
    location = result.get("geometry").get("location")
    return location["lat"], location["lng"]


def get_result(g_result) -> Optional[Dict[str, any]]:
    """
    checks to see if the parameter is a valid geocode result
    and returns the first entry if so
    """
    if not isinstance(g_result, list) and not isinstance(g_result, dict):
        raise ValueError("g_result was neither a list or a dict")

    if isinstance(g_result, list):
        if len(g_result) == 0:
            return None
        else:
            return g_result[0]

    return g_result
