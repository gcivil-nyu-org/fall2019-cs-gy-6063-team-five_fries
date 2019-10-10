import requests
import json
import xmltodict

from secret import getZwsId

def getRentalHouse(address, cityStateZip, rentZestimate):

    GET_SEARCH_RESULTS = "https://www.zillow.com/webservice/GetSearchResults.htm"
    ZWSID = getZwsId()
    if len(ZWSID) == 0:
        print("ZWSID is empty")
    elif len(cityStateZip) == 0:
        print("citystateZip is empty")
    else:
        #xmlResponse = requests.get("http://www.zillow.com/webservice/GetSearchResults.htm?zws-id=X1-ZWz17lpszuaux7_anh8k&address=3rd+Ave&citystatezip=Brooklyn%2C+NY&rentzestimate=true")
        xmlResponse = requests.get(GET_SEARCH_RESULTS, params={'zws-id': ZWSID, 'address': address, 'citystatezip': cityStateZip, 'rentzestimate': rentZestimate})
        str = json.dumps(xmltodict.parse(xmlResponse.content))
        replacestr = ['-', '#', '@']    # replace special character in response
        for i in replacestr:
            str = str.replace(i,'')
        return str
    #return json.dumps(xmltodict.parse(xmlResponse.content))


if __name__ == "__main__":
    data = json.loads(getRentalHouse("3rd Ave", "Brooklyn, NY", "true"))

    for result in (data['SearchResults:searchresults']['response']['results']['result']):
        print("!!!!")
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
        print(amount["text"], amount["currency"])
        updatetime = rentzestimate['lastupdated']
        print(updatetime)

        if "valuechange" in rentzestimate.keys():
            valuechange = rentzestimate['valuechange']
            print(valuechange)
        if "valuationrange" in rentzestimate.keys():
            lowvalue = rentzestimate['valuationrange']['low']
            highvalue = rentzestimate['valuationrange']['high']
            print(highvalue)
