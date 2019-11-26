import googlemaps
from secret import get_google_api_key
from typing import Dict, List


def fetch_geocode(
    address, components=None, bounds=None, region=None, language=None
) -> List[Dict[str, any]]:

    results = googlemaps.Client(key=get_google_api_key()).geocode(
        address, components, bounds, region, language
    )
    if not results:
        return []

    results[0]["postal"] = ""
    addr_list = results[0]["address_components"]
    for addr in addr_list:
        for type in addr["types"]:
            if type == "postal_code":
                results[0]["postal"] = addr["long_name"]

    return results


def fetch_reverse_geocode(
    latlng, result_type=None, location_type=None, language=None
) -> List[Dict[str, any]]:

    results = googlemaps.Client(key=get_google_api_key()).reverse_geocode(
        latlng, result_type, location_type, language
    )
    results[0]["postal"] = ""
    addr_list = results[0]["address_components"]
    for addr in addr_list:
        for type in addr["types"]:
            if type == "postal_code":
                results[0]["postal"] = addr["long_name"]

    return results
