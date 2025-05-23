from imap_tools import MailBox, AND
from dotenv import load_dotenv
import os

load_dotenv()

# Dados da sua conta Gmail
EMAIL = os.getenv("IMAP_MAIL")
SENHA = os.getenv("IMAP_PWD")

with MailBox("imap.gmail.com").login(EMAIL, SENHA, initial_folder="INBOX") as mailbox:
    for msg in mailbox.fetch(AND(seen=True), limit=5, reverse=True):
        print("De:", msg.from_)
        print("Assunto:", msg.subject)
        print("Texto:", msg.text)
        print("---")