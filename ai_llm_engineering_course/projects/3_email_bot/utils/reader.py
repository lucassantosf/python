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

# Escopo para ler e modificar emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

# Dados da sua conta Gmail
class EmailReader:
    def __init__(self):
        self.service = self.authenticate_gmail()
        
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

    def read_emails(self, max_results=10, query='is:unread'):
        """Lê os e-mails e retorna uma lista simplificada com os campos relevantes"""
        threads = self.list_threads(self.service, max_results=max_results, query=query)

        emails = []
        for thread in threads:
            messages = self.get_thread_messages(self.service, thread['id'])

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
                    'message_id': message_id,  # Message-ID do cabeçalho
                    'id': message['id']  # ID interno do Gmail para operações como marcar como lido
                }
                emails.append(email)
        return emails

    def find_email_by_message_id(self, message_id):
        """Busca um e-mail específico pelo message_id no Gmail"""
        try:
            query = f"rfc822msgid:{message_id}"
            results = self.service.users().messages().list(userId="me", q=query).execute()
            messages = results.get('messages', [])

            if not messages:
                return None

            # Pega o primeiro resultado (deve ser único)
            msg_id = messages[0]['id']
            msg = self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()

            headers = {header['name']: header['value'] for header in msg['payload']['headers']}
            message_id = headers.get('Message-ID')

            return {
                "from": headers.get('From'),
                "subject": headers.get('Subject'),
                "message_id": message_id,
                "thread_id": msg.get('threadId'),
                "id": msg_id  # Adicionando o ID interno do Gmail para uso em outras operações
            }
        except Exception as e:
            print(f"Erro ao buscar e-mail por message_id: {e}")
            return None
            
    def mark_as_read(self, message_id=None, thread_id=None):
        """
        Marca um email ou thread como lido no Gmail
        
        Args:
            message_id (str, optional): ID da mensagem específica a ser marcada como lida
            thread_id (str, optional): ID da thread a ser marcada como lida
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
            
        Note:
            Pelo menos um dos parâmetros (message_id ou thread_id) deve ser fornecido
        """
        try:
            if not message_id and not thread_id:
                print("Erro: É necessário fornecer message_id ou thread_id")
                return False
                
            # Se temos o ID da mensagem, usamos ele diretamente
            if message_id:
                result = self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                print(f"Email marcado como lido: {result.get('id')}")
                return True
                
            # Se temos apenas o thread_id, precisamos buscar todas as mensagens da thread
            elif thread_id:
                # Buscar todas as mensagens da thread
                thread = self.service.users().threads().get(userId='me', id=thread_id).execute()
                messages = thread.get('messages', [])
                
                # Marcar cada mensagem como lida
                for message in messages:
                    msg_id = message.get('id')
                    self.service.users().messages().modify(
                        userId='me',
                        id=msg_id,
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                
                print(f"Thread inteira marcada como lida: {thread_id} ({len(messages)} mensagens)")
                return True
                
        except Exception as e:
            print(f"ERRO: Erro ao marcar email/thread como lido: {e}")
            return False


def main():

    reader = EmailReader()

    print("Buscando threads recentes não lidas...")
    threads = reader.list_threads(reader.service, max_results=1, query='is:unread')

    for thread in threads:
        print(f"\nThread ID: {thread['id']}")
        messages = reader.get_thread_messages(reader.service, thread['id'])

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
