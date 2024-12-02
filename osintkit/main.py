import json
import argparse
import osintkit.whois as whois
import osintkit.geoip as geoip
import osintkit.iplookup as iplookup
import osintkit.arecord as arecord
import osintkit.screenshot as screenshot
import osintkit.helper as helper

def main_template(request_function):
    """
    A template function for executing a request function manually from the command line.

    Args:
        request_function (function): The function to be executed with the input argument.

    Returns:
        None

    Raises:
        None

    Example:
    >>> python3 osintkit/<datarequest>.py <input>
    """
    import sys
    import json
    script_name = sys.argv[0]
    if any(arg in sys.argv for arg in ["help", "-h", "--help"]):
        print(f"Usage: python3 {script_name} <domain/ip/string/file/mailheader>")
        exit()

    if len(sys.argv) > 1:
        input = sys.argv[1]
        response = request_function(input)
        response = json.dumps(response, indent=4)
        print(response)
    else:
        print(f"Usage: python3 {script_name} <domain/ip/string/file/mailheader>")


def main():
    parser = argparse.ArgumentParser(description="OSINT Kit")
    required = parser.add_mutually_exclusive_group(required=True)

    required.add_argument("--whois", type=str, metavar="", help="Perform a whois lookup on a domain or IP address")
    required.add_argument("--iplookup", type=str, metavar="", help="Perform an IP lookup on a domain or IP address")
    required.add_argument("--geoip", type=str, metavar="", help="Perform a GeoIP lookup on a domain or IP address")
    required.add_argument("--arecord", type=str, metavar="", help="Perform an A record lookup on a domain")
    required.add_argument("--screenshot", type=str, metavar="", help="Take a screenshot of a website and also generate a PDF")

    optional = parser.add_argument_group()
    optional.add_argument(
        "-f", "--format",
        metavar="",
        help="Print the output in a specific format. Default json. [string|markdown]"
    )
    optional.add_argument(
        "-o", "--output",
        nargs="?",
        metavar="",
        const=True,
        help="Save the output to a file"
    )



    args = parser.parse_args()

    response = None
    if args:
        if args.whois:
            response = whois.request(args.whois)
        if args.iplookup:
            response = iplookup.request(args.iplookup)
        if args.arecord:
            response = arecord.request(args.arecord)
        if args.geoip:
            response = geoip.request(args.geoip)
        if args.screenshot:
            response = screenshot.request(args.screenshot)

        if response:
            if args.format:
                if args.output:
                    if args.output is True: args.output = "osintkit_output"
                    helper.save_to_file(response, args.output, args.format)
                else:
                    if args.format == "string":
                        print(helper.json_to_string(response))
                    elif args.format == "markdown":
                        print(helper.json_to_string(response, markdown=True))
            else:
                print(json.dumps(response, indent=4))
        else:
            print("No data available.")
    else:
        parser.print_help()
        print("Usage: osintkit --arg <domain/ip>")

if __name__ == "__main__":
    main()
