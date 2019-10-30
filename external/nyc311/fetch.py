from sodapy import Socrata
import requests
import pandas as pd
from secret import get_311_socrata_key
from .models import NYC311Complaint
from typing import List, Dict


def fetch_311_data(
    zip, max_query_results=None, num_entries_to_search=10000, t_out=10
) -> Dict[str, any]:
    nyc_311_dataset_domain = "data.cityofnewyork.us"
    nyc_311_dataset_identifier = "fhrw-4uyv"
    try:
        nyc_311_dataset_token = get_311_socrata_key()
    except KeyError:
        nyc_311_dataset_token = (
            None  # works with None but lower number of requests can be made
        )

    client = Socrata(nyc_311_dataset_domain, nyc_311_dataset_token)

    client.timeout = t_out

    try:
        return client.get(
            nyc_311_dataset_identifier,
            select="created_date, incident_zip, incident_address, city, complaint_type, descriptor, status",
            # q=str(zip), #uncomment if want to query directly on the server side (may lead to timeout)
            order="created_date DESC",
            limit=num_entries_to_search,
        )
    except requests.exceptions.Timeout:
        raise TimeoutError


def fetch_311_data_as_dataframe(
    zip, max_query_results=None, num_entries_to_search=10000, t_out=10
) -> pd.DataFrame:
    results = fetch_311_data(zip, max_query_results, num_entries_to_search, t_out)
    return pd.DataFrame.from_records(results)


def get_311_data(
    zip, max_query_results=None, num_entries_to_search=10000, t_out=10
) -> List[NYC311Complaint]:
    """Returns results based on a zip code. Validation for the zip code is done on the front-end.
    Timeout exception is raised if timeout period expires. Default timeout period is 10 seconds."""

    query_results = None
    results_df = fetch_311_data_as_dataframe(
        zip, max_query_results, num_entries_to_search, t_out
    )
    results_df = results_df.loc[results_df["incident_zip"] == str(zip)]

    if max_query_results and len(results_df) > max_query_results:
        results_df = results_df[:max_query_results]

    query_results = [NYC311Complaint(**dic) for dic in results_df.to_dict("records")]

    return query_results
