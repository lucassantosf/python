from __future__ import print_function
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

# Escopo para ler emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Dados da sua conta Gmail
class EmailReader:
    def authenticate_gmail(self):
        """Faz a autenticação com OAuth2 e retorna o serviço da Gmail API"""
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('./credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('gmail', 'v1', credentials=creds)
        return service

    def list_threads(self, service, max_results=5):
        """Lista as threads (conversas) recentes"""
        threads = service.users().threads().list(userId='me', maxResults=max_results).execute().get('threads', [])
        return threads

    def get_thread_messages(self, service, thread_id):
        """Retorna todas as mensagens de uma thread"""
        thread = service.users().threads().get(userId='me', id=thread_id, format='full').execute()
        return thread['messages']

    def parse_message(self, message):
        """Extrai o texto da mensagem"""
        parts = message['payload'].get('parts', [])
        body = ''
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                body = base64.urlsafe_b64decode(data).decode()
            elif part['mimeType'] == 'text/html':
                data = part['body'].get('data', '')
                html = base64.urlsafe_b64decode(data).decode()
                soup = BeautifulSoup(html, 'html.parser')
                body = soup.get_text()
        return body.strip()

def main():

    reader = EmailReader()
    service = reader.authenticate_gmail()

    print("Buscando threads recentes...")
    threads = reader.list_threads(service, max_results=5)

    for thread in threads:
        print(f"\nThread ID: {thread['id']}")
        messages = reader.get_thread_messages(service, thread['id'])

        for i, message in enumerate(messages):
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            subject = headers.get('Subject', 'Sem assunto')
            from_ = headers.get('From', 'Desconhecido')
            text = reader.parse_message(message)

            print(f"\n📧 Email {i+1}")
            print(f"De: {from_}")
            print(f"Assunto: {subject}")
            print(f"Corpo:\n{text}")

if __name__ == "__main__": 
    main()