import json
from typing import Dict, List
import os


def fetch_craigslist_housing(*, limit, **kwargs) -> List[Dict[str, any]]:
    filepath = os.path.join(os.path.dirname(__file__), "sample-response.json")
    with open(filepath) as f:
        return json.loads(f.read())
