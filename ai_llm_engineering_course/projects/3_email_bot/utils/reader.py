from imap_tools import MailBox, AND
from dotenv import load_dotenv
import os

load_dotenv()

# Dados da sua conta Gmail
class EmailReader:
    def __init__(self, params):
        self.params = params
        self.email = os.getenv("MAILER_ADDRESS")
        self.password = os.getenv("MAILER_PWD")
        self.seen = params.get("seen", False)

    def read_emails(self):
        emails = []
        with MailBox("imap.gmail.com").login(self.email, self.password, initial_folder="INBOX") as mailbox:
            for msg in mailbox.fetch(AND(seen=self.seen), limit=10, reverse=True):
                emails.append({
                    "id": msg.uid,
                    "from": msg.from_,
                    "subject": msg.subject,
                    "text": msg.text,
                    "raw": msg,
                }) 
        return emails