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

    def list_threads(self, service, max_results=1, query=None):
        """Lista as threads (conversas) recentes, com opção de filtro"""
        threads = service.users().threads().list(userId='me', maxResults=max_results, q=query).execute().get('threads', [])
        return threads

    def get_thread_messages(self, service, thread_id):
        """Retorna todas as mensagens de uma thread"""
        thread = service.users().threads().get(userId='me', id=thread_id, format='full').execute()
        return thread['messages']

    def extract_body(self, payload):
        """Extrai recursivamente o conteúdo do corpo da mensagem"""
        if 'parts' in payload:
            for part in payload['parts']:
                # Caso o part seja 'text/plain'
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    data = part['body']['data']
                    return base64.urlsafe_b64decode(data).decode().strip()
                # Caso o part seja 'text/html'
                elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                    data = part['body']['data']
                    html = base64.urlsafe_b64decode(data).decode()
                    soup = BeautifulSoup(html, 'html.parser')
                    return soup.get_text().strip()
                # Caso o part tenha mais partes dentro dele (multipart/alternative, etc)
                else:
                    result = self.extract_body(part)
                    if result:
                        return result
        else:
            # Se não houver 'parts', tentar pegar o body direto
            if 'body' in payload and 'data' in payload['body']:
                data = payload['body']['data']
                if data:
                    return base64.urlsafe_b64decode(data).decode().strip()

        return ''  # Retorna vazio se nada encontrado

    def parse_message(self, message):
        """Wrapper para chamar o parser recursivo"""
        return self.extract_body(message['payload'])

    def read_emails(self, max_results=5, query='is:unread'):
        """Lê os e-mails e retorna uma lista simplificada com os campos relevantes"""
        service = self.authenticate_gmail()
        threads = self.list_threads(service, max_results=max_results, query=query)

        emails = []
        for thread in threads:
            messages = self.get_thread_messages(service, thread['id'])

            for message in messages:
                headers = {h['name']: h['value'] for h in message['payload']['headers']}
                subject = headers.get('Subject', 'Sem assunto')
                from_ = headers.get('From', 'Desconhecido')
                message_id = headers.get('Message-ID')  # Extraindo o Message-ID
                text = self.parse_message(message)

                email = {
                    'from': from_,
                    'subject': subject,
                    'text': text,
                    'thread_id': message['threadId'],
                    'message_id': message_id  # Adicionando o Message-ID
                }
                emails.append(email)
        return emails

def main():

    reader = EmailReader()
    service = reader.authenticate_gmail()

    print("Buscando threads recentes não lidas...")
    threads = reader.list_threads(service, max_results=1, query='is:unread')

    for thread in threads:
        print(f"\nThread ID: {thread['id']}")
        messages = reader.get_thread_messages(service, thread['id'])

        for i, message in enumerate(messages):
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            subject = headers.get('Subject', 'Sem assunto')
            from_ = headers.get('From', 'Desconhecido')
            text = reader.parse_message(message)

            print(f"\nEmail {i+1}")
            print(f"De: {from_}")
            print(f"Assunto: {subject}")
            print(f"Corpo:\n{text[:50]}")

if __name__ == "__main__": 
    main()