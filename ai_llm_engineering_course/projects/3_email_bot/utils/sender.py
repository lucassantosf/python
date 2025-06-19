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
        """
        Envia um email simples usando a API do Gmail
        
        Args:
            to_address (str): Endereço de email do destinatário
            subject (str): Assunto do email
            body (str): Corpo do email
            
        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário
        """
        message = MIMEMultipart()
        message["To"] = to_address
        message["From"] = self.email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        try:
            response = self.service.users().messages().send(
                userId="me",
                body={"raw": raw_message}
            ).execute()
            
            # Verificar se a resposta contém um ID de mensagem (indicando sucesso)
            if response and 'id' in response:
                print(f"E-mail enviado com sucesso! ID: {response['id']}")
                return True
            else:
                print("Aviso: E-mail enviado, mas sem ID de confirmação.")
                return True  # Ainda consideramos como sucesso se não houver erro
        except Exception as e:
            print("Erro ao enviar e-mail:", e)
            return False

    def reply_email(self, original_msg, reply_body, content_type="plain"):
        """
        Responde um e-mail usando a API do Gmail
        
        Args:
            original_msg (dict): Dicionário com informações do email original
            reply_body (str): Corpo da resposta
            content_type (str, optional): Tipo de conteúdo (plain ou html). Defaults to "plain".
            
        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário
        """

        # Validação dos campos essenciais
        required_fields = ["from_", "subject", "thread_id"]
        missing_fields = [field for field in required_fields if not original_msg.get(field)]

        if missing_fields:
            print(f"Erro: Campos ausentes no e-mail original: {', '.join(missing_fields)}")
            return False

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
            response = self.service.users().messages().send(
                userId="me",
                body={"raw": raw_message, "threadId": original_msg["thread_id"]}
            ).execute()
            
            # Verificar se a resposta contém um ID de mensagem (indicando sucesso)
            if response and 'id' in response:
                print(f"Resposta enviada com sucesso! ID: {response['id']}")
                return True
            else:
                print("Aviso: Resposta enviada, mas sem ID de confirmação.")
                return True  # Ainda consideramos como sucesso se não houver erro
                
        except HttpError as error:
            print(f"Erro na API do Gmail: {error}")
            return False
        except Exception as e:
            print(f"Erro inesperado ao enviar resposta: {e}")
            return False
