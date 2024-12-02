import requests
import osintkit.helper as helper

api_dict = {
    "ipwho.is": "http://ipwho.is/{ip}?output=json",
    "ipapi.com": "http://ip-api.com/json/{ip}",
    "ipapi.co": "http://ipapi.co/{ip}/json/",
    "freegeoip.live": "http://freegeoip.live/json/{ip}",
    #"hackertarget.com": "https://api.hackertarget.com/ipgeo/?q={ip}",
}

def query_api(api, ip):
    try:
        """Query an API with the given IP. API string format: http://example.com/{placeholder}/otherstuff"""
        api_url = api_dict[api].format(ip=ip)
        user_agent = "Mozilla/5.0"  # Some APIs require a user agent else they block the request
        response = requests.get(api_url, headers={"User-Agent": user_agent})
        return response.json() if response.status_code == 200 else ["Error Statuscode " + str(response.status_code)]
    except:
        return ["Exception"]





def filter_response(json_response):
    """Filter and rename keys from the API response."""
    valid_keys = [
        "country",
        "region",
        "state",
        "city",
        "latitude",
        "longitude"
    ]
    rename_keys = {
        "country_name": "country",
        "region_name": "region",
        "lat": "latitude",
        "lon": "longitude",
    }
    filtered_response = {}
    for key, value in json_response.items():
        if key in valid_keys:
            filtered_response[key] = value
        elif key in rename_keys:
            filtered_response[rename_keys[key]] = value
    return filtered_response





def convert_coords_to_url(json_response):
    """Add a link to opentopomap by latitude and longitude for each response."""
    topo_url = "https://opentopomap.org/#marker=7/{latitude}/{longitude}"
    topo_url = topo_url.format(latitude=json_response["latitude"], longitude=json_response["longitude"])
    del json_response["latitude"]
    del json_response["longitude"]
    # sort keys alphabetically and append url
    json_response = {key: json_response[key] for key in sorted(json_response.keys())}
    json_response["url"] = topo_url
    return json_response





def request(input):
    """Request data from all APIs, build json response and hand over."""
    domain, ip = helper.get_primary(input)
    if not ip:
        return "N/A"
    response = {}
    for api in api_dict:
        api_data = query_api(api, ip)
        if "Error Statuscode" not in str(api_data):
            api_data = filter_response(api_data)
            api_data = convert_coords_to_url(api_data)
            response[api] = api_data
        else:
            response[api] = api_data
    return response





if __name__ == "__main__":
    from osintkit.main import main_template
    main_template(request)
