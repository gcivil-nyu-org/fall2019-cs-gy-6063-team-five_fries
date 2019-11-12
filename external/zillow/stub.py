import json
from typing import Dict, List
import os


def fetch_zillow_housing(
    *, address, city_state=None, zipcode=None, show_rent_z_estimate
) -> List[Dict[str, any]]:
    filepath = os.path.join(
        os.path.dirname(__file__), "sample-response/fetch_zillow_housing.json"
    )
    with open(filepath) as f:
        return json.loads(f.read())


all_zillow_response_names = [
    "zillow-normal.xml",
    "zillow-error.xml",
    "zillow-single.xml",
    "zillow-without-estimate.xml",
]


def get_zillow_response(name) -> str:
    filepath = os.path.join(os.path.dirname(__file__), "sample-response", name)
    with open(filepath) as f:
        return f.read()


def get_all_zillow_response() -> List[str]:
    return [get_zillow_response(name) for name in all_zillow_response_names]
