import os
import shlex
from dotenv import load_dotenv
import time
import smtplib
import imaplib

import threading

import osintbot.datarequest as datarequest
from osintbot.MailRequest import MailRequest
from osintbot.MailResponse import MailResponse
import osintbot.log as log

import osintkit.helper as kit_helper

class Mailbot:

    IMAP = None
    SMTP = None

    MAIL_FETCH_INTERVAL = 30 # seconds
    MAIL_PROCESS_INTERVAL = 60 # seconds

    MAIL_SENDER = {} # stores sender and amount of emails do check rate limit // sender gets deleted after MAIL_RATE_LIMIT_INTERVAL seconds

    MAIL_LAST_RATE_LIMIT_TIME = 0 # time of the last rate limit check
    MAIL_RATE_LIMIT = 4 # amount of emails
    MAIL_RATE_LIMIT_INTERVAL = 60 # seconds
    MAIL_EXPIRE = 360 # seconds

    MAIL_QUEUE = []

    # initialize the mailbot
    def __init__(self, env_instance, db_instance):
        self.mail_expire = 360
        self.connection_expire = 3600
        self.env_instance = env_instance
        self.db_instance = db_instance
        self.mail_run()





    # start the subprocesses for checking and processing mails
    def mail_run_new(self):
        check_mail_thread = threading.Thread(target=self.mail_check_new)
        process_mail_thread = threading.Thread(target=self.mail_process_new)
        check_mail_thread.start()
        process_mail_thread.start()
        check_mail_thread.join()
        process_mail_thread.join()





    # fetch mails and filter them
    def mail_check_new(self):
        current_time = time.time()
        self.imap_connect()
        while True:
            mail_request_list = self.fetch_email()
            # store all mails in the database
            for mail in mail_request_list:
                self.db_instance.mail_insert(False, mail.MAIL_TIME, mail.MAIL_FROM, mail.MAIL_SUBJECT, mail.REQUEST_FUNCTION, mail.REQUEST_TARGET)
            # filter mails
            mail_request_list = self.mail_filter_new(mail_request_list)
            # add remaining mails to the mail queue
            for mail in mail_request_list:
                self.MAIL_QUEUE.append(mail)
            # periodically reconnect to the IMAP server
            if time.time() - current_time > self.connection_expire:
                log.log("mail", f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Connection expired. Reconnecting to IMAP server {self.env_instance.imap_server}.")
                self.imap_disconnect()
                current_time = time.time()
                self.imap_connect()
            time.sleep(self.MAIL_FETCH_INTERVAL)
    
    # process the mail queue
    def mail_process_new(self):
        while True:
            if not self.MAIL_QUEUE.empty():
                mail = self.MAIL_QUEUE.pop(0)
                log.log("mail", f"Processing email: {mail.MAIL_ID} - time: {mail.MAIL_TIME}, from: {mail.MAIL_FROM}, subject: {mail.MAIL_SUBJECT}, jobs: {len(mail.REQUEST_TARGET)}")
                mail_response = MailResponse()
                mail_response.set_sender(self.env_instance.mail_user)
                mail_response.set_receiver(mail.MAIL_FROM)
                mail_response.set_subject(f'osintbot response to: {mail.MAIL_SUBJECT} for {len(mail.REQUEST_TARGET)} jobs')
                mail_response.set_content(self.run_function(mail))
                self.send_email(mail_response)
                self.delete_email([mail])
                # wait MAIL_PROCESS_INTERVAL seconds before processing the next mail
                time.sleep(self.MAIL_PROCESS_INTERVAL)
            # if no mails are in the queue, wait MAIL_FETCH_INTERVAL seconds before checking again
            time.sleep(self.MAIL_FETCH_INTERVAL)





    # filter the mails
    def mail_filter_new(self, mail_list: list) -> list:

        def filter_limit(mail_request: MailRequest) -> str:
            if any(queue_mail.MAIL_FROM == mail_request.MAIL_FROM for queue_mail in self.MAIL_QUEUE):
                request_status = f"--> Limit for simultaneous jobs exceeded. From: {mail_request.MAIL_FROM}, Subject: {mail_request.MAIL_SUBJECT}, Time: {mail_request.MAIL_TIME}"
                return request_status
            else:
                return True
        
        # rate limit means that the same sender can only send MAIL_RATE_LIMIT mails per MAIL_RATE_LIMIT_INTERVAL seconds
        def filter_rate_limit(mail_request: MailRequest) -> str:
            current_time = time.time()
            if current_time - self.MAIL_LAST_RATE_LIMIT_TIME > self.MAIL_RATE_LIMIT_INTERVAL:
                self.MAIL_SENDER = {}
                self.MAIL_LAST_RATE_LIMIT_TIME = current_time
            else:
                if mail_request.MAIL_FROM in self.MAIL_SENDER:
                    if self.MAIL_SENDER[mail_request.MAIL_FROM] >= self.MAIL_RATE_LIMIT:
                        request_status = f"--> Rate limit exceeded. From: {mail_request.MAIL_FROM}, Subject: {mail_request.MAIL_SUBJECT}, Time: {mail_request.MAIL_TIME}"
                        return request_status
                    else:
                        self.MAIL_SENDER[mail_request.MAIL_FROM] += 1
                        return True
                else:
                    self.MAIL_SENDER[mail_request.MAIL_FROM] = 1
                    return True
        
        # expired means that a mail is only valid for MAIL_EXPIRE seconds
        def filter_expired(mail_request: MailRequest) -> str:
            if time.time() - time.mktime(time.strptime(mail_request.MAIL_TIME, '%d-%b-%Y %H:%M:%S')) > self.mail_expire:
                request_status = f"--> Expired email {mail_request.MAIL_ID}. From: {mail_request.MAIL_FROM}, Subject: {mail_request.MAIL_SUBJECT}, Time: {mail_request.MAIL_TIME}"
                self.db_instance.mail_refused(mail_request.MAIL_TIME, mail_request.MAIL_FROM, mail_request.MAIL_SUBJECT)
                return request_status
            else:
                return True
            
        # invalid means that the mail does not contain a valid request that violates the rules
        def filter_invalid(mail_request: MailRequest) -> bool:
                if not mail_request.REQUEST_STATUS:
                    request_status = f"--> Invalid email {mail_request.MAIL_ID}. From: {mail_request.MAIL_FROM}, Subject: {mail_request.MAIL_SUBJECT}, Time: {mail_request.MAIL_TIME}"
                    self.db_instance.mail_refused(mail_request.MAIL_TIME, mail_request.MAIL_FROM, mail_request.MAIL_SUBJECT)
                    return request_status
                else:
                    return True

        filtered_mails = []
        for mail in mail_list:
            request_status = None
            request_status = filter_limit(mail)
            if not isinstance(request_status, str):
                request_status = filter_rate_limit(mail)
            if not isinstance(request_status, str):
                request_status = filter_expired(mail)
            if not isinstance(request_status, str):
                request_status = filter_invalid(mail)
            if isinstance(request_status, str):
                log.log("mail", request_status)
                self.db_instance.mail_refused(mail.MAIL_TIME, mail.MAIL_FROM, mail.MAIL_SUBJECT)
                filtered_mails.append(mail)
        return [mail for mail in mail_list if mail not in filtered_mails]


            
            

    def imap_connect(self):
        while Exception:
            try:
                self.IMAP = imaplib.IMAP4_SSL(self.env_instance.imap_server)
                self.IMAP.login(self.env_instance.mail_user, self.env_instance.mail_password)
                break
            except Exception as e:
                log.exception("mail", "IMAP connection failed", e)
                time.sleep(60)
    def imap_disconnect(self):
        try:
            self.IMAP.close()
            self.IMAP.logout()
        except Exception as e:
            log.exception("mail", "IMAP disconnection failed", e)

    def smtp_connect(self):
        while Exception:
            try:
                self.SMTP = smtplib.SMTP(self.env_instance.smtp_server, self.env_instance.smtp_port)
                self.SMTP.starttls()
                self.SMTP.login(self.env_instance.mail_user, self.env_instance.mail_password)
                break
            except Exception as e:
                log.exception("mail", "SMTP connection failed", e)
                time.sleep(60)
    def smtp_disconnect(self):
        try:
            self.SMTP.quit()
        except Exception as e:
            log.exception("mail", "SMTP disconnection failed", e)





    def delete_email(self, mail_list: list) -> None:
        try:
            for mail in mail_list:
                self.IMAP.store(mail.MAIL_ID, '+FLAGS', '\\Deleted')
            self.IMAP.expunge()
            log.log("mail", f"--> Emails deleted successfully: {len(mail_list)}") if mail_list else None
        except Exception as e:
            log.exception("mail", "Email failed to delete", e)

    def send_email(self, mail: MailResponse):
        try:
            self.smtp_connect()
            self.SMTP.sendmail(mail.mail['From'], mail.mail['To'], mail.mail.as_string())
            self.SMTP.quit()
            log.log("mail", f"--> Response sent successfully. To: {mail.mail['To']}, Subject: {mail.mail['Subject']}")
        except Exception as e:
            log.exception("mail", f"Email failed to send. To: {mail.mail['To']}, Subject: {mail.mail['Subject']}", e)

    def fetch_email(self):
        try:
            self.IMAP.select('inbox')
            status, messages = self.IMAP.search(None, '(TO ' + self.env_instance.mail_user + ')')
            messages = messages[0].split()
            mail_list = []
            for mail_id in messages:
                mail_payload = self.IMAP.fetch(mail_id, '(RFC822)')[1][0][1].decode('utf-8')
                mail_list.append(MailRequest(mail_id, mail_payload))
                # sort per time, newest last
                mail_list.sort(key=lambda x: time.mktime(time.strptime(x.MAIL_TIME, '%d-%b-%Y %H:%M:%S')))
            return mail_list
        except Exception as e:
            log.exception("mail", "Email failed to fetch", e)





    HELP = "Available commands:\n" \
    " whois <domain/ip> - Retrieve whois data for a domain or IP address\n" \
    " iplookup <domain/ip> - Retrieve IP lookup data for a domain or IP address\n" \
    " geoip <domain/ip> - Retrieve GeoIP data for a domain or IP address\n" \
    " arecord <domain> - Retrieve A record data for a domain\n" \
    " report <domain/ip> - Retrieve all available data for a domain or IP address\n" \
    " screenshot <url> - Take a full-page screenshot of a URL and receive the image + printable A4 PDF\n" \
    "\n" \
    "Write a single request in the subject line or the body and multiple requests in the body.\n" \
    "Example single subject request: 'subject = whois example.com'\n" \
    "Example single body request: 'subject = whois, body = example.com'\n" \
    "Example multiple body request: 'subject = whois, body = example.com <newline> example.net <newline> example.org'\n"

    FUNCTIONS = {
        'help' : None,
        'whois': datarequest.single_report,
        'geoip': datarequest.single_report,
        'iplookup': datarequest.single_report,
        'arecord': datarequest.single_report,
        'report': datarequest.full_report,
        'screenshot': datarequest.file_output_report
    }
    def run_function(self, mail_request: MailRequest):
        try:
            if mail_request.REQUEST_FUNCTION == 'help':
                return self.HELP
            response = []
            function = self.FUNCTIONS[mail_request.REQUEST_FUNCTION]
            for target in mail_request.REQUEST_TARGET:
                log.log("mail", f"--> Running function: '{mail_request.REQUEST_FUNCTION}' with input: '{target}'")
                result = function(input=target, function=mail_request.REQUEST_FUNCTION)
                response.append({"target": target, "result": result})
                time.sleep(10)
            return kit_helper.json_to_string(response)
        except Exception as e:
            log.exception("mail", f"Function failed to run: '{mail_request.REQUEST_FUNCTION}'", e)




def main():
    if os.path.isfile('.env'):
        load_dotenv(dotenv_path='.env')
    Mailbot()

if __name__ == '__main__':
    main()
