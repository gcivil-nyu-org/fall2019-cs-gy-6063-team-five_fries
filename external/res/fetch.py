from sodapy import Socrata
import requests
import pandas as pd
from .models import ResComplaint
from typing import List, Dict


def fetch_res_data(
    zip, max_query_results=20, num_entries_to_search=10000, t_out=10
) -> Dict[str, any]:
    nyc_res_dataset_domain = "data.cityofnewyork.us"
    nyc_res_dataset_identifier = "43nn-pn8j"
    nyc_res_dataset_token = (
        None  # works with None but lower number of requests can be made
    )

    client = Socrata(nyc_res_dataset_domain, nyc_res_dataset_token)

    client.timeout = t_out

    try:
        return client.get(
            nyc_res_dataset_identifier,
            select="dba, boro, zipcode, violation_description",
            # q=str(zip), #uncomment if want to query directly on the server side (may lead to timeout)
            order="score DESC",
            limit=num_entries_to_search,
        )
    except requests.exceptions.Timeout:
        raise TimeoutError


def fetch_res_data_as_dataframe(
    zip, max_query_results=None, num_entries_to_search=10000, t_out=10
) -> pd.DataFrame:
    results = fetch_res_data(zip, max_query_results, num_entries_to_search, t_out)
    return pd.DataFrame.from_records(results)


def get_res_data(
    zip, max_query_results=None, num_entries_to_search=10000, t_out=10
) -> List[ResComplaint]:
    """Returns results based on a zip code. Validation for the zip code is done on the front-end.
    Timeout exception is raised if timeout period expires. Default timeout period is 10 seconds."""

    query_results = None
    results_df = fetch_res_data_as_dataframe(
        zip, max_query_results, num_entries_to_search, t_out
    )
    results_df = results_df.loc[results_df["zipcode"] == str(zip)]
    results_df = pd.DataFrame.dropna(results_df)

    if max_query_results and len(results_df) > max_query_results:
        results_df = results_df[:max_query_results]

    query_results = [
        ResComplaint.from_dict(dic) for dic in results_df.to_dict("records")
    ]

    return query_results
