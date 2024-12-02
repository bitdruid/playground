import os
import re
import html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import osintbot.log as log

class MailResponse:

    def __init__(self):
        self.mail = MIMEMultipart()

    def set_sender(self, sender):
        self.mail['From'] = sender

    def set_receiver(self, receiver):
        self.mail['To'] = receiver

    def set_subject(self, subject):
        self.mail['Subject'] = subject

    def set_body(self, body):
        self.mail.attach(MIMEText(self.convert_plain_to_html(body), 'html'))   

    def set_content(self, response_contents):
        try:
            
            # if there is only one response, check if it is a file or text
            if isinstance(response_contents, dict):

                if isinstance(response_contents['result'], list):
                    for file_path in response_contents['result']:
                        self.attach_file(file_path)
                elif not os.path.isfile(response_contents['result']):
                    self.mail.attach(MIMEText(response_contents['result'], 'plain'))
                else:
                    self.attach_file(response_contents['result'])

            # if there are multiple responses, check if they are files or text
            if isinstance(response_contents, list):
                
                for entry in response_contents:
                    if isinstance(entry['result'], list): # add all results of the entry in list as attachments
                        for file_path in entry['result']:
                            self.attach_file(file_path)
                    elif os.path.isfile(entry['result']): # add the single result of the entry as attachment if it is a file
                        self.attach_file(entry['result'])
                    else:
                        self.attach_text(entry['target'], entry['result']) # add the single result of the entry as text file

            # if a plain text is passed, set it as the body
            else:
                self.set_body(response_contents)

        except Exception as e:
            log.exception("mail", "Error parsing response-mail content", e)

    # attach a text as text file to the mail
    def attach_text(self, target, result):
        attachment = MIMEText(result, 'plain')
        attachment.add_header('Content-Disposition', f"attachment; filename={target}.txt")
        self.mail.attach(attachment)

    # attach a file to the mail
    def attach_file(self, file_path):
        attachment = MIMEApplication(open(file_path, 'rb').read())
        attachment.add_header('Content-Disposition', f"attachment; filename={os.path.basename(file_path)}")
        self.mail.attach(attachment)
        os.remove(file_path)

    def convert_plain_to_html(self, plain_text):
        plain_text = html.escape(plain_text)
        plain_text = plain_text.replace('\n', '<br>')
        plain_text = plain_text.replace('\t', '&emsp;')
        plain_text = plain_text.replace(' ', '&nbsp;')
        url_pattern = re.compile(r'(https?://[^\s]+)')
        plain_text = url_pattern.sub(r'<a href="\1">\1</a>', plain_text)
        html_text = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    white-space: pre-wrap; /* This handles spaces and line breaks */
                }}
            </style>
        </head>
        <body>
            {plain_text}
        </body>
        </html>
        """
        return html_text
