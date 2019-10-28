import math
import pandas as pd
from .get_311_data import fetch_311_data_as_dataframe


def get_311_statistics(query_zip, num_entries_to_search=10000, t_out=10):
    """Returns noise and illegal parking statistics based on a zip code.
    Validation for the zip code is done on the front-end.
    Timeout exception is raised if timeout period expires.
    Default timeout period is 10 seconds."""

    results_df = fetch_311_data_as_dataframe(
        query_zip, None, num_entries_to_search, t_out
    )
    results_df = results_df.dropna()
    # results are grouped by complaint type
    complaint_type_df_dict = dict(tuple(results_df.groupby("complaint_type")))
    # all the different complaint types are stored in this list
    unique_complaint_type_list = results_df["complaint_type"].unique().tolist()
    # Since "noisy" violations might have different descriptions (e.g. Noisy - Park, Noisy - Party etc.)
    # in the dataset, all the relevant categories are combined
    noisy_complaint_types = [
        complaint
        for complaint in unique_complaint_type_list
        if ("nois" or "loud") in complaint.lower()
    ]
    parking_complaint_types = [
        complaint
        for complaint in unique_complaint_type_list
        if "parking" in complaint.lower()
    ]
    complaint_type_lists = [noisy_complaint_types, parking_complaint_types]

    complaint_types_queried = ["Noise", "Parking"]
    complaint_results = []

    for idx, complaint_type_list in enumerate(complaint_type_lists):
        # only the relevant types of complaints are selected (e.g. only noise complaints)
        complaint_dfs = [
            complaint_type_df_dict[complaint_type]
            for complaint_type in complaint_type_list
        ]
        complaint_dfs_concatenated = pd.concat(complaint_dfs)
        # The dataframe (which contains only complaints for a specific type e.g. noise)
        # are further grouped by zip code).
        unique_zip_codes_list = (
            complaint_dfs_concatenated["incident_zip"].unique().tolist()
        )
        zip_codes_df_dict = dict(
            tuple(complaint_dfs_concatenated.groupby("incident_zip"))
        )
        # Most notorious neighborhood and number of complaints for the specific complaint type (e.
        # are recorded.
        max_complaints = 0
        for zip in unique_zip_codes_list:
            if len(zip_codes_df_dict[zip]) > max_complaints:
                max_complaints_zip = zip
                max_complaints = len(zip_codes_df_dict[zip])
        # if the queried zip code has any violations of that type (e.g. noise)
        if str(query_zip) in zip_codes_df_dict:
            complaints_query_zip_df = zip_codes_df_dict[str(query_zip)]
            # total complaints of the desired type (e.g. noise) in the zip code of interest
            total_complaints_query_zip = len(complaints_query_zip_df)
            # complaints of the desired type in the zip code of interest that were closed
            closed_complaints_query_zip = len(
                dict(tuple(complaints_query_zip_df.groupby("status")))["Closed"]
            )
            percentage_complaints_closed = (
                closed_complaints_query_zip / total_complaints_query_zip
            ) * 100
            percentage_complaints_closed = round(percentage_complaints_closed, 2)
            # complaint level is calculated on a scale of 0 - 5 where 5 is assigned to the most
            # notorious neighborhood (calculated above)
            complaint_level = math.ceil(
                (total_complaints_query_zip / max_complaints) * 5
            )  # 0 - 5
        else:
            total_complaints_query_zip = 0
            closed_complaints_query_zip = 0
            percentage_complaints_closed = 0
            complaint_level = 0

        tmp = {
            "complaint_type": complaint_types_queried[idx],
            "complaint_level": complaint_level,
            "total_complaints_query_zip": total_complaints_query_zip,
            "closed_complaints_query_zip": closed_complaints_query_zip,
            "percentage_complaints_closed": percentage_complaints_closed,
            "max_complaints": max_complaints,
            "max_complaints_zip": max_complaints_zip,
        }
        complaint_results.append(tmp)

    return complaint_results


if __name__ == "__main__":
    try:
        complaint_results = get_311_statistics(10009)  # valid zip code
    except TimeoutError:
        print("Timeout")

    print("RESULTS FOR VALID ZIP CODE:")
    print("No matches =", len(complaint_results) == 0)
    for result in complaint_results:
        print(result)
        print("------------------")
    print("------------------")

    try:
        complaint_results = get_311_statistics(100099)  # valid zip code
    except TimeoutError:
        print("Timeout")

    print("RESULTS FOR INVALID ZIP CODE:")
    print("No matches =", len(complaint_results) == 0)
    for result in complaint_results:
        print(result)
        print("------------------")
    print("------------------")
