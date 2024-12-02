import requests
import socket
import osintkit.helper as helper
import osintkit.whois as whois

def iplookup(ip, domain):
    """Query on ipinfo."""
    ip_json = {}
    if ip:
        try:
            ip_json["primary ipv4"] = ip
            ip_json["primary ipv6"] = socket.getaddrinfo(ip, None, socket.AF_INET6)[0][4][0]
        except:
            pass
        api_data = requests.get(f"http://ipinfo.io/{ip}/json").json()
        if "hostname" in api_data: ip_json["Hostname"] = api_data["hostname"]
        if "country" in api_data: ip_json["Country"] = api_data["country"]
        if "org" in api_data: ip_json["ASN and ISP"] = api_data["org"]
    if domain:
        whois_data = whois.request(domain)
        if "registrar" in whois_data: ip_json["registrar"] = whois_data["registrar"] 
        if "network" in whois_data: ip_json["network"] = whois_data["network"]
    return ip_json if ip_json else "N/A"

def request(input):
    """Return iplookup data."""
    domain, ip = helper.get_primary(input)
    return iplookup(ip, domain)

if __name__ == "__main__":
    from osintkit.main import main_template
    main_template(request)
