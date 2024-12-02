import shlex
import time
import email
import osintbot.log as log

class MailRequest:
    
    MAIL_ID = None
    MAIL_TIME = None
    MAIL_FROM = None
    MAIL_SUBJECT = None
    MAIL_BODY = None

    REQUEST_FUNCTION = None
    REQUEST_TARGET = []
    REQUEST_STATUS = None

    def __init__(self, mail_id, mail_full):
        try:
            self.MAIL_ID = mail_id
            self.MAIL_TIME = mail_full.split('Date: ')[1].split('\r\n')[0].strip()
            self.MAIL_TIME = time.strftime('%d-%b-%Y %H:%M:%S', time.strptime(self.MAIL_TIME, '%a, %d %b %Y %H:%M:%S %z'))
            self.MAIL_FROM = mail_full.split('From: ')[1].split('\r\n')[0].strip()
            self.MAIL_FROM = self.MAIL_FROM.split('<')[1].split('>')[0] if '<' in self.MAIL_FROM else self.MAIL_FROM
            self.MAIL_SUBJECT = mail_full.split('Subject: ')[1].split('\r\n')[0].strip()

            # plain text body to prevent errors with html content
            msg = email.message_from_string(mail_full, policy=email.policy.default)
            plain_text_body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        plain_text_body = part.get_content()
                        break
            else:
                plain_text_body = msg.get_content()

            self.MAIL_BODY = plain_text_body.strip()

            self.MAIL_ATTACHMENTS = []
            self.MAIL_ATTACHMENTS = [a.split('Content-Disposition: form-data; name="attachment"; filename="')[1].split('"')[0] for a in mail_full.split('attachment; filename="')[1:]]
            self.validate_request()
        except Exception as e:
            log.exception("mail", "Error parsing request-mail content", e)

    def validate_request(self):
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~:/?#[]@!$&'()*+,;="
        request_status = True
        request = self.MAIL_SUBJECT.split(' ')
        target = []

        if len(request) == 0:
            request_status = "No query args in mail subject"
            log.log("mail", request_status)
        elif len(request) == 1:
            target = self.MAIL_BODY.splitlines() if self.MAIL_BODY else []
            if len(target) > 5:
                request_status = "Too many query args in mail body"
                log.log("mail", request_status)
        elif len(request) == 2:
            target = [request[1]]
        elif len(request) > 2:
            request_status = "Too many query args in mail subject"
            log.log("mail", request_status)

        function = request[0].lower()
        target = [item.lower() for item in target]

        if not all(c in allowed_chars for c in function):
            request_status = "Invalid characters in function"
            log.log("mail", request_status)

        for item in target:
            if not all(c in allowed_chars for c in item):
                request_status = "Invalid characters in query args"
                log.log("mail", request_status)

        if isinstance(request_status, bool):
            if function in self.FUNCTIONS:
                self.REQUEST_FUNCTION = shlex.quote(function)
                self.REQUEST_TARGET = [shlex.quote(item) for item in target]
                self.REQUEST_STATUS = True
            else:
                log.log("mail", f"Invalid request function: '{function}'")
                self.REQUEST_STATUS = False
        else:
            self.REQUEST_STATUS = False
