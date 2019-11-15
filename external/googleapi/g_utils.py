def parse_lat_lng(geo_result_obj):
    """
    Parses out a latitude/longitude tuple from the Google Geocoder response object
    """
    if geo_result_obj:
        if "geometry" in geo_result_obj.keys():
            geo = geo_result_obj["geometry"]
            if "location" in geo.keys():
                location = geo_result_obj["geometry"]["location"]
                return (location["lat"], location["lng"])

    # default case if there was no result returned
    return (None, None)
