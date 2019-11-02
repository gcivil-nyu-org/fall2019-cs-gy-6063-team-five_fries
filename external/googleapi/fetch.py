import googlemaps
from secret import get_google_api_key
from typing import Dict, List


def fetch_geocode(
    address, components=None, bounds=None, region=None, language=None
) -> List[Dict[str, any]]:

    print("------------------CALLING FETCH---------------")
    gmaps = googlemaps.Client(key=get_google_api_key())
    # coder = Geocoder(api_key=get_google_api_key())
    # result = coder.geocode(str(req))
    results = gmaps.geocode(address, components, bounds, region, language)
    return results
