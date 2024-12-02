import osintkit.helper as helper
import dns.resolver

def request(input):
    domain = helper.ip_to_domain(input)
    if not domain:
        return "N/A"
    
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']

    response = {}

    try:
        response["A"] = [str(record) for record in resolver.resolve(domain, "A")]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        pass

    try:
        response["AAAA"] = [str(record) for record in resolver.resolve(domain, "AAAA")]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        pass

    return response if any(response.values()) else "N/A"

if __name__ == "__main__":
    from osintkit.main import main_template
    main_template(request)

