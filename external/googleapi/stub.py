import json
from typing import Dict, List
import os


def fetch_geocode(
    address, components=None, bounds=None, region=None, language=None
) -> List[Dict[str, any]]:

    filepath = os.path.join(os.path.dirname(__file__), "sample-response-geocode.json")
    with open(filepath) as f:
        return json.loads(f.read())


def fetch_geocode_no_zip(
    address, components=None, bounds=None, region=None, language=None
) -> List[Dict[str, any]]:

    filepath = os.path.join(os.path.dirname(__file__), "sample-response-no-zip.json")
    with open(filepath) as f:
        return json.loads(f.read())


def fetch_geocode_no_type(
    address, components=None, bounds=None, region=None, language=None
) -> List[Dict[str, any]]:

    filepath = os.path.join(
        os.path.dirname(__file__), "sample-response-geocode-no-types.json"
    )
    with open(filepath) as f:
        return json.loads(f.read())


def fetch_reverse_geocode(
    latlng, result_type=None, location_type=None, language=None
) -> List[Dict[str, any]]:

    filepath = os.path.join(os.path.dirname(__file__), "sample-response-geocode.json")
    with open(filepath) as f:
        return json.loads(f.read())


def fetch_reverse_geocode_no_zip(
    address, components=None, bounds=None, region=None, language=None
) -> List[Dict[str, any]]:

    filepath = os.path.join(os.path.dirname(__file__), "sample-response-no-zip.json")
    with open(filepath) as f:
        return json.loads(f.read())
