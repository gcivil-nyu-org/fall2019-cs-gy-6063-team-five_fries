from sodapy import Socrata
import requests
import pandas as pd
from secret import get_311_socrata_key


def get_311_data(zip, max_query_results=5, num_entries_to_search=10000, t_out=10):
    """Returns results based on a zip code. Validation for the zip code is done on the front-end.
    Timeout exception is raised if timeout period expires. Default timeout period is 10 seconds."""

    nyc_311_dataset_domain = "data.cityofnewyork.us"
    nyc_311_dataset_identifier = "fhrw-4uyv"
    try:
        nyc_311_dataset_token = get_311_socrata_key()
    except KeyError:
        nyc_311_dataset_token = (
            None
        )  # works with None but lower number of requests can be made

    client = Socrata(nyc_311_dataset_domain, nyc_311_dataset_token)

    client.timeout = t_out

    query_results = None
    timeout = False
    no_matches = True

    try:
        results = client.get(
            nyc_311_dataset_identifier,
            select="created_date, incident_zip, incident_address, city, complaint_type, descriptor, status",
            # q=str(zip), #uncomment if want to query directly on the server side (may lead to timeout)
            order="created_date DESC",
            limit=num_entries_to_search,
        )

        results_df = pd.DataFrame.from_records(results)
        results_df = results_df.loc[results_df["incident_zip"] == str(zip)]

        if len(results_df) > 0:
            no_matches = False

        if len(results_df) > max_query_results:
            results_df = results_df[:max_query_results]

        query_results = results_df.to_dict("records")

    except requests.exceptions.Timeout:
        timeout = True

    return query_results, timeout, no_matches


if __name__ == "__main__":
    query_results, timeout, no_matches = get_311_data(10009)  # valid zip code
    print(type(query_results))
    print(len(query_results))
    print(query_results)
    print(timeout)
    print(no_matches)

    query_results, timeout, no_matches = get_311_data(100099)  # invalid zip code
    print(type(query_results))
    print(len(query_results))
    print(query_results)
    print(timeout)
    print(no_matches)
