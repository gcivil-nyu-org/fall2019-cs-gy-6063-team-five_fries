import requests
import json
import xmltodict

from secret import get_zws_id


def get_rental_house(address, city_state_zip, rent_z_estimate):

    get_search_results = "https://www.zillow.com/webservice/GetSearchResults.htm"
    zwsid = get_zws_id()
    if not zwsid:
        print("zwsid is empty")
    elif not city_state_zip:
        print("citystateZip is empty")
    else:
        xml_response = requests.get(
            get_search_results,
            params={
                "zws-id": zwsid,
                "address": address,
                "citystatezip": city_state_zip,
                "rentzestimate": rent_z_estimate,
            },
        )
        str = json.dumps(xmltodict.parse(xml_response.content))
        replacestr = ["-", "#", "@"]  # replace special character in response
        for i in replacestr:
            str = str.replace(i, "")
        return str


# Run this part while local testing
if __name__ == "__main__":
    data = json.loads(get_rental_house("3rd Ave", "Brooklyn, NY", "true"))

    for result in data["SearchResults:searchresults"]["response"]["results"]["result"]:
        print("--- The Next Result ---")
        zpid = result["zpid"]

        links = result["links"]
        homedetails = links["homedetails"]
        mapthishome = links["mapthishome"]
        comparables = links["comparables"]

        address = result["address"]
        street = address["street"]
        zipcode = address["zipcode"]

        rentzestimate = result["rentzestimate"]
        amount = rentzestimate["amount"]
        print("Rent: ", amount["text"], amount["currency"])
        updatetime = rentzestimate["lastupdated"]
        print("Update Time:", updatetime)

        # TODO: Unavaialbe to get these three datas
        if "valuechange" in rentzestimate.keys():
            valuechange = rentzestimate["valuechange"]
            print("Value Change: ", valuechange)
        if "valuationrange" in rentzestimate.keys():
            lowvalue = rentzestimate["valuationrange"]["low"]
            highvalue = rentzestimate["valuationrange"]["high"]
            print("The highest Rent:", highvalue)
