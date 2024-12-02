import os
import osintkit.helper as helper

def whois(domain: str) -> str:
    """Retrieve whois data for a domain"""
    whois_data = os.popen("whois " + domain).read().lower()
    return whois_data if any(term in whois_data for term in ["domain name:", "netname:", "restricted rights", "reg-name:"]) else False

def whois_search_term(domain: str, term: str, whois_data=None, all=False) -> str:
    """Search for a specific term in the whois data"""
    terms = []
    if whois_data is None:
        whois_data = whois(domain)
    if whois_data is not False and term in whois_data:
        if all:
            terms = [line.split(term)[1].strip() for line in whois_data.split("\n") if term in line]
            return list(set(terms))
        else:
            term = whois_data.split(term)[1].split("\n")[0].strip()
            return term if term else False
    return False

def request(domain: str) -> dict:
    """
    Retrieves WHOIS data for a given domain and extracts specific information from it.
    """
    if not helper.validate_primary(domain):
        return False

    whois_data = whois(domain)
    if not whois_data:
        return "N/A"

    result = {}

    search_terms = {
        "creation_date": "creation date:",
        "registrar": "registrar:",
        "network": "netname:",
        "organization": "organization:"
    }

    for key, term in search_terms.items():
        value = whois_search_term(domain, term, whois_data)
        if value:
            result[key] = value

    result["whois"] = whois_data if whois_data else "N/A"
    return result

if __name__ == "__main__":
    from osintkit.main import main_template
    main_template(request)
