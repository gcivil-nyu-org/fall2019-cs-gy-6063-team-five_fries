import json
from typing import Dict, List
import os


def fetch_zillow_housing(
    *, address, city_state=None, zipcode=None, show_rent_z_estimate
) -> List[Dict[str, any]]:
    filepath = os.path.join(os.path.dirname(__file__), "sample-response.json")
    with open(filepath) as f:
        return json.loads(f.read())


def get_zillow_error_response() -> str:
    filepath = os.path.join(os.path.dirname(__file__), "sample-response-error.xml")
    with open(filepath) as f:
        return f.read()


def get_zillow_response() -> str:
    filepath = os.path.join(os.path.dirname(__file__), "sample-response.xml")
    with open(filepath) as f:
        return f.read()
