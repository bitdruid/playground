import ipaddress
import socket
import requests
import json


def check_online_offline(domain):
    """Check if a domain is online or offline."""
    try:
        response = requests.head(domain)
        return response.ok
    except requests.exceptions.RequestException:
        return False


def validate_domain(domain):
    """Validate if a domain is given."""
    try:
        ipaddress.ip_address(domain)
        return False
    except ValueError:
        domain_parts = domain.split(".")
        if len(domain_parts) > 1 and len(domain_parts[-1]) > 1:
            return True
        else:
            return False


def validate_ip(ip):
    """Validate if an IP address is given."""
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private:
            #print("Private IP address given.")
            return False
        return True
    except ValueError:
        return False


def validate_primary(input: str) -> bool:
    """
    Validate if a given input is a domain or IP address.

    Parameters:
    - input (str): The domain or IP address to validate.

    Returns:
    - bool: True if the input is a domain or IP address, False if not.
    """
    return validate_domain(input) or validate_ip(input)


def domain_to_ip(domain: str) -> str:
    try:
        if validate_ip(domain):
            return domain
        ip = socket.gethostbyname(domain)
        if validate_ip(ip):
            return ip
        else:
            return False
    except socket.gaierror:
        return False


def ip_to_domain(ip: str) -> str:
    try:
        if validate_domain(ip):
            return ip
        domain = socket.gethostbyaddr(ip)[0]
        if validate_domain(domain):
            return domain
        else:
            return False
    except socket.herror:
        return False


def get_primary(input: str) -> tuple:
    """
    Returns the primary domain and IP for a given domain or IP.

    Parameters:
    - input (str): The domain or IP to check.

    Returns:
    - tuple: [0] domain, [1] IP
    - bool: False, False if no domain or IP is given
    """
    if validate_domain(input):
        ip = domain_to_ip(input)
        return input, ip
    elif validate_ip(input):
        domain = ip_to_domain(input)
        return domain, input
    return False, False



def json_to_string(json_input: str, markdown: bool = False) -> str:
    """
    Converts a JSON object to a formatted string representation.

    Parameters:
        json_input (str): The JSON object to be converted. Can be a dictionary or a string.
        markdown (bool, optional): Specifies whether the output should be formatted using markdown syntax. Defaults to False.

    Returns:
        str: The formatted string representation of the JSON object.

    Notes:
        - If the 'json_input' is not a dictionary, it is returned as is with a newline character appended.
        - If 'markdown' is True, the output is formatted using markdown syntax, otherwise it is formatted using plain text syntax.
        - If the 'json_input' is a dictionary, the keys and values are formatted as follows:
            - Keys are displayed in bold (if markdown is True) or as is (if markdown is False), followed by a colon.
            - Values are displayed based on their type:
                - If the value is a dictionary, the subkeys and subvalues are displayed as key-value pairs.
                - If the value is a list, each item is displayed on a separate line.
                - If the value is a string, it is displayed as is.
        - Each key-value pair is displayed within code blocks (if markdown is True) or without code blocks (if markdown is False).
        - A newline character is added after each key-value pair, except for the last one.

    Examples:
        >>> json_input = '{"name": "John", "age": 30, "city": "New York"}'
        >>> json_to_string(json_input)
        'name:\nJohn\n\nage:\n30\n\ncity:\nNew York\n'
        
        >>> json_input = {"name": "John", "age": 30, "city": "New York"}
        >>> json_to_string(json_input, markdown=True)
        '***name:***\n```\nJohn\n```\n\n***age:***\n```\n30\n```\n\n***city:***\n```\nNew York\n```\n'
    """
    if not isinstance(json_input, dict):
        return json_input
    
    count_keys = len(json_input.keys())
    current_key = 1
    message_parts = []
    for key, value in json_input.items():
        message_parts.append(f"***{key}:***\n" if markdown else f"{key}:\n")
        message_parts.append("```\n" if markdown else "")
        
        if isinstance(value, dict):
            message_parts.extend([f"{subkey}: {subvalue}\n" for subkey, subvalue in value.items()])
        elif isinstance(value, list):
            message_parts.extend([f"{item}\n" for item in value])
        elif isinstance(value, str):
            message_parts.append(f"{value}\n")
        
        if current_key == count_keys:
            message_parts.append("")
        else:
            message_parts.append("\n")

        message_parts.append("```\n" if markdown else "")
        current_key += 1
    return "".join(message_parts)



def save_to_file(json_input: dict, path: str, format: str) -> None:
    """
    Save the JSON output to a file.

    Args:
        json_input (dict): The JSON object to be saved to a file.
        path (str): The path of the file where the JSON output will be saved.
        format (str): The format in which the JSON output should be saved (string, CSV, or JSON).

    Returns:
        None. The function saves the JSON output to a file.
    """
    try:
        if format == "string":
            path = path + ".txt"
            output = json_to_string(json_input)
        if format == "markdown":
            path = path + ".md"
            output = json_to_string(json_input, markdown=True)
        else:
            path = path + ".json"
            output = json.dumps(json_input, indent=4)

        with open(path, "w") as file:
            file.write(output)

        print(f"Output saved to {path}")
    except Exception as e:
        print(f"Error saving output to {path}: {str(e)}")
