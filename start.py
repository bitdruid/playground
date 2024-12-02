import os
import threading
import dotenv
import subprocess
import osintbot.mail_bot as mail_bot
import osintbot.discord_bot as discord_bot
import osintbot.db as db

if __name__ == "__main__":

    class Environment:

        DISCORD_BOT = False
        MAIL_BOT = False

        def __init__(self):
            if os.path.isfile('.env'):
                print(f"Loading .env file: {os.path.abspath('.env')}")
                dotenv.load_dotenv(dotenv_path='.env')
            self.admin_mail = os.getenv('ADMIN_MAIL') or None
            self.web_log = True if os.getenv('WEB_LOG', '').lower() == 'true' else False
            self.web_sqlite = True if os.getenv('WEB_SQLITE', '').lower() == 'true' else False
            self.discord_bot()
            self.mail_bot()

        def discord_bot(self):
            try:
                self.bot_token = os.getenv('BOT_TOKEN')
                if self.bot_token is None:
                    raise ValueError('No bot token provided')
                self.bot_name = os.getenv('BOT_NAME') or "osintbot"
                self.bot_channel = os.getenv('BOT_CHANNEL') or "osint"
                self.DISCORD_BOT = True
            except ValueError as e:
                print(e)

        def mail_bot(self):
            try:
                self.mail_user = os.getenv('MAIL_USER')
                if self.mail_user is None:
                    raise ValueError('No email provided')
                self.mail_password = os.getenv('MAIL_PASS')
                if self.mail_password is None:
                    raise ValueError('No password provided')
                self.smtp_server = os.getenv('MAIL_SMTP_SERVER')
                if self.smtp_server is None:
                    raise ValueError('No SMTP server provided')
                self.smtp_port = os.getenv('MAIL_SMTP_PORT')
                if self.smtp_port is None:
                    raise ValueError('No SMTP port provided')
                self.imap_server = os.getenv('MAIL_IMAP_SERVER')
                if self.imap_server is None:
                    raise ValueError('No IMAP server provided')
                self.imap_port = os.getenv('MAIL_IMAP_PORT')
                if self.imap_port is None:
                    raise ValueError('No IMAP port provided')
                self.MAIL_BOT = True
            except ValueError as e:
                print(e)

    env_instance = Environment()
    db_instance = db.Database()
    if env_instance.web_log:
        web_log_thread = threading.Thread(
            target=subprocess.check_call,
            args=(["python3", "weblog.py"],),
            kwargs={"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL},
        )
        web_log_thread.start()
        #web_log_thread.join()
    if env_instance.web_sqlite:
        sqlite_web_thread = threading.Thread(
            target=subprocess.check_call,
            args=(
                [
                    "sqlite_web",
                    "--no-browser",
                    "--host=0.0.0.0",
                    "--port=5002",
                    "database/osintbot.sqlite",
                ],
            ),
            kwargs={"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL},
        )
        sqlite_web_thread.start()
        #sqlite_web_thread.join()

    # start mail_bot
    if env_instance.MAIL_BOT:
        mailbot_instance = mail_bot.Mailbot(env_instance, db_instance)
        mail_thread = threading.Thread(target=mailbot_instance)
        mail_thread.start()
        mail_thread.join()

    # # start discord_bot
    # if env_instance.DISCORD_BOT:
    #     discord_instance = discord_bot.main(env_instance, db_instance)
    #     discord_thread = threading.Thread(target=discord_instance)
    #     discord_thread.start()
    #     discord_thread.join()
