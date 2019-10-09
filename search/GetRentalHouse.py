import requests
import json
import xmltodict

from secret import getZwsId

def GetRentalHouse(address, cityStateZip, rentZestimate):
    def getStatus():
        return xmlResponse.status_code
    def getContentText():
        return xmlResponse.text

    GET_SEARCH_RESULTS = "https://www.zillow.com/webservice/GetSearchResults.htm"
    ZWSID = getZwsId()
    if len(ZWSID) == 0:
        print("ZWSID is empty")
    elif len(cityStateZip) == 0:
        print("citystateZip is empty")
    else:
        #xmlResponse = requests.get("http://www.zillow.com/webservice/GetSearchResults.htm?zws-id=X1-ZWz17lpszuaux7_anh8k&address=3rd+Ave&citystatezip=Brooklyn%2C+NY&rentzestimate=true")
        xmlResponse = requests.get(GET_SEARCH_RESULTS, params={'zws-id': ZWSID, 'address': address, 'citystatezip': cityStateZip, 'rentzestimate': rentZestimate})

    return json.dumps(xmltodict.parse(xmlResponse.content))
