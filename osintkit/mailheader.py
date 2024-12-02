import email
import os.path


def request(input):
    if os.path.isfile(input):
        with open(input, "r") as f:
            header = email.message_from_file(f)
    else:
        header = email.message_from_string(input)
    if header:
        header = email.parser.HeaderParser().parsestr(str(header))
        received = header.get_all("Received")
        sender = email.utils.parseaddr(header.get("From"))[1]
        sender_domain = sender.split("@")[1]
        #mail_route = {
        #    "timestamp": timestamp,
        #    "from": ip/hostname,
        #    "by": ip/hostname,
        #    "for": ip/hostname,
        #    "with": protocol,
        #    "id": id,
        #    "via": ip/hostname,
        #    "spf-result": result,
        #}
        __import__("pprint").pprint(f"Sender: {sender}\nSender-Domain: {sender_domain}\nReceived:\n{received}")
        return "To be implemented in the future..."



if __name__ == "__main__":
    from osintkit.main import main_template
    main_template(request)
