import requests
import json
import xmltodict

from secret import getZwsId

def getRentalHouse(address, cityStateZip, rentZestimate):

    GET_SEARCH_RESULTS = "https://www.zillow.com/webservice/GetSearchResults.htm"
    ZWSID = getZwsId()
    if not ZWSID:
        print("ZWSID is empty")
    elif not cityStateZip:
        print("citystateZip is empty")
    else:
        xmlResponse = requests.get(GET_SEARCH_RESULTS, params={'zws-id': ZWSID, 'address': address, 'citystatezip': cityStateZip, 'rentzestimate': rentZestimate})
        str = json.dumps(xmltodict.parse(xmlResponse.content))
        replacestr = ['-', '#', '@']    # replace special character in response
        for i in replacestr:
            str = str.replace(i,'')
        return str


# Run this part while local testing
if __name__ == "__main__":
    data = json.loads(getRentalHouse("3rd Ave", "Brooklyn, NY", "true"))

    for result in (data['SearchResults:searchresults']['response']['results']['result']):
        print("--- The Next Result ---")
        zpid = result['zpid']

        links = result['links']
        homedetails = links['homedetails']
        mapthishome = links['mapthishome']
        comparables = links['comparables']

        address = result['address']
        street = address['street']
        zipcode = address['zipcode']

        rentzestimate = result['rentzestimate']
        amount = rentzestimate['amount']
        print("Rent: ", amount["text"], amount["currency"])
        updatetime = rentzestimate['lastupdated']
        print("Update Time:", updatetime)

        # TODO: Unavaialbe to get these three datas
        if "valuechange" in rentzestimate.keys():
            valuechange = rentzestimate['valuechange']
            print("Value Change: ",valuechange)
        if "valuationrange" in rentzestimate.keys():
            lowvalue = rentzestimate['valuationrange']['low']
            highvalue = rentzestimate['valuationrange']['high']
            print("The highest Rent:", highvalue)
