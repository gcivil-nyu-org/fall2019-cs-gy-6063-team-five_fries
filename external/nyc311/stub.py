import json
from typing import Dict
import os


def fetch_311_data(
    zip, max_query_results=None, num_entries_to_search=10000, t_out=10
) -> Dict[str, any]:
    filepath = os.path.join(os.path.dirname(__file__), "sample-response.json")
    with open(filepath) as f:
        return json.loads(f.read())


def fetch_311_data_closed(
    zip, max_query_results=None, num_entries_to_search=10000, t_out=10
) -> Dict[str, any]:
    filepath = os.path.join(os.path.dirname(__file__), "sample-response-closed.json")
    with open(filepath) as f:
        return json.loads(f.read())


def fetch_311_data_single(
    zip, max_query_results=None, num_entries_to_search=10000, t_out=10
) -> Dict[str, any]:
    filepath = os.path.join(os.path.dirname(__file__), "sample-response-single.json")
    with open(filepath) as f:
        return json.loads(f.read())
