from secret import get_zws_id
import requests
import xmltodict
from typing import List, Dict
from .models import ZillowHousingResponse


def fetch_zillow_housing(
    *, zwsid=None, address, city_state=None, zipcode=None, show_rent_z_estimate
) -> List[Dict[str, any]]:
    zwsid = zwsid or get_zws_id()
    if not zwsid:
        raise Exception("No ZWSID")

    if not city_state and not zipcode:
        raise Exception("either city_state or zipcode should be given")

    get_search_results = "https://www.zillow.com/webservice/GetSearchResults.htm"
    xml_response = requests.get(
        get_search_results,
        params={
            "zws-id": zwsid,
            "address": address,
            "citystatezip": city_state or zipcode,
            "rentzestimate": "true" if show_rent_z_estimate else "false",
        },
    )
    dic = dict(xmltodict.parse(xml_response.content))
    return dic["SearchResults:searchresults"]["response"]["results"]["result"]


def get_zillow_housing(
    *, address, city_state=None, zipcode=None, show_rent_z_estimate=True
) -> List[ZillowHousingResponse]:
    results = fetch_zillow_housing(
        address=address,
        city_state=city_state,
        zipcode=zipcode,
        show_rent_z_estimate=show_rent_z_estimate,
    )
    return [ZillowHousingResponse.from_zillow_response(dic) for dic in results]
