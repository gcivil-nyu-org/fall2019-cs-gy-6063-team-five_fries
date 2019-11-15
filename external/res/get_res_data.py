from sodapy import Socrata
import requests
import pandas as pd


def get_res_data(zip, max_query_results=20, num_entries_to_search=2000, t_out=10):

    res_dataset_domain = "data.cityofnewyork.us"
    res_dataset_identifier = "43nn-pn8j"
    res_dataset_token = None  # works with None but lower number of requests can be made
    client = Socrata(res_dataset_domain, res_dataset_token)

    client.timeout = t_out

    results = None
    query_results = None
    timeout = False
    no_matches = True
    try:
        results = client.get(
            res_dataset_identifier,
            select="dba, boro, zipcode, violation_description",
            order="score DESC",
            limit=num_entries_to_search,
        )
        results_df = pd.DataFrame.from_records(results)
        results_df = pd.DataFrame.dropna(results_df)
        results_df = results_df.loc[results_df["zipcode"] == str(zip)]
        if len(results_df) > 0:
            no_matches = False
        if len(results_df) > max_query_results:
            results_df = results_df[:max_query_results]
        query_results = results_df.to_dict("records")
    except requests.exceptions.Timeout:
        timeout = True
    return query_results, timeout, no_matches


if __name__ == "__main__":
    query_results, timeout, no_matches = get_res_data(10009)  # valid zip code
    print(type(query_results))
    print(len(query_results))
    print(query_results)
    print(timeout)
    print(no_matches)
    query_results, timeout, no_matches = get_res_data(100099)  # invalid zip code
    print(type(query_results))
    print(len(query_results))
    print(query_results)
    print(timeout)
    print(no_matches)
