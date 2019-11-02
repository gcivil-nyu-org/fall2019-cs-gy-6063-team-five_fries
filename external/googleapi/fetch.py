import googlemaps
from secret import get_google_api_key
from typing import Dict, List


def fetch_geocode(
    address, components=None, bounds=None, region=None, language=None
) -> List[Dict[str, any]]:

    print("------------------CALLING FETCH---------------")
    # gmaps = googlemaps.Client(key=get_google_api_key())

    # results = gmaps.geocode(address, components, bounds, region, language)
    results = googlemaps.Client(key=get_google_api_key()).geocode(
        address, components, bounds, region, language
    )
    addr_list = results[0]["address_components"]
    for addr in addr_list:
        for type in addr["types"]:
            if type == "postal_code":
                results[0]["postal"] = addr["long_name"]

    print(f"RESULTS: {results}")
    return results
