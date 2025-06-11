from __future__ import print_function
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
from utils.reader import EmailReader
import os

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class EmailSender:
    def __init__(self):
        self.email = os.getenv("SEEDER_INCIDENTS_RECEIVER_EMAIL")   
        self.service = self.authenticate_gmail()

    def authenticate_gmail(self):
        """Autentica na API do Gmail"""
        creds = None
        if os.path.exists('token_send.json'):
            creds = Credentials.from_authorized_user_file('token_send.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('./credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token_send.json', 'w') as token:
                token.write(creds.to_json())

        service = build('gmail', 'v1', credentials=creds)
        return service

    def send_email(self, to_address, subject, body):
        """Envia um email simples usando a API do Gmail"""
        message = MIMEMultipart()
        message["To"] = to_address
        message["From"] = self.email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        try:
            self.service.users().messages().send(
                userId="me",
                body={"raw": raw_message}
            ).execute()
            print("E-mail enviado com sucesso!")
        except Exception as e:
            print("Erro ao enviar e-mail:", e)

    def reply_email(self, original_msg, reply_body, content_type="plain"):
        """Responde um e-mail usando a API do Gmail"""

        # Validação dos campos essenciais
        required_fields = ["from_", "subject", "thread_id"]
        missing_fields = [field for field in required_fields if not original_msg.get(field)]

        if missing_fields:
            print(f"Erro: Campos ausentes no e-mail original: {', '.join(missing_fields)}")
            return

        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = original_msg["from_"]
        msg["Subject"] = "Re: " + original_msg["subject"]

        message_id = original_msg.get("headers", {}).get("Message-ID")
        if message_id:
            msg["In-Reply-To"] = message_id
            msg["References"] = message_id

        msg.attach(MIMEText(reply_body, content_type))

        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        try:
            self.service.users().messages().send(
                userId="me",
                body={"raw": raw_message, "threadId": original_msg["thread_id"]}
            ).execute()
            print("Resposta enviada com sucesso!")
        except HttpError as error:
            print(f"Erro na API do Gmail: {error}")
        except Exception as e:
            print(f"Erro inesperado ao enviar resposta: {e}")