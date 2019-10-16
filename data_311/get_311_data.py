import os
from sodapy import Socrata
import requests

def get_311_data(zip):

    nyc_311_dataset_domain = 'data.cityofnewyork.us'
    nyc_311_dataset_identifier = 'fhrw-4uyv'
    # nyc_311_dataset_token = None
    nyc_311_dataset_token = "u5UpvoQyF4fXvTACZwjf9gI3o"

    client = Socrata(nyc_311_dataset_domain, nyc_311_dataset_token)

    client.timeout = 10

    results = None
    error = False

    try:
        results = client.get(nyc_311_dataset_identifier,
                             select="created_date, incident_zip, incident_address, city, complaint_type, descriptor, status",
                             q=str(zip),
                             order = "created_date DESC",
                             limit =5)

    except requests.exceptions.Timeout:
        error = True

    return results, error


