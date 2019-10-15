import os
from sodapy import Socrata
import requests

nyc_311_dataset_domain = 'data.cityofnewyork.us'
nyc_311_dataset_identifier = 'fhrw-4uyv'

# nyc_311_dataset_token = None
nyc_311_dataset_token = "u5UpvoQyF4fXvTACZwjf9gI3o"

client = Socrata(nyc_311_dataset_domain, nyc_311_dataset_token)

client.timeout = 10

try:
    results = client.get(nyc_311_dataset_identifier,
#                          select="created_date, incident_zip, complaint_type, descriptor, status, city, resolution_description, incident_address",
                        select="created_date, incident_zip, incident_address, city, complaint_type, descriptor, status",
                         q="11218",
                         order = "created_date DESC",
                        limit =5)
    print(len(results))
    for i in range(3):
        print(results[i])
except requests.exceptions.Timeout:
    print("Timeout occurred")
