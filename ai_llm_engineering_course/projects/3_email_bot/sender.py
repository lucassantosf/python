import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

class EmailSender:
    def __init__(self, smtp_server=None, smtp_port=None, email=None, password=None):
        self.smtp_server = smtp_server or "smtp.gmail.com"
        self.smtp_port = smtp_port or 587
        self.email = email or os.getenv("IMAP_MAIL")
        self.password = password or os.getenv("IMAP_PWD")

    def send_email(self, to_address, subject, body):
        # Cria o corpo da mensagem
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Envia o e-mail via SMTP
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
                print("✅ E-mail enviado com sucesso.")
        except Exception as e:
            print("❌ Erro ao enviar e-mail:", e)

# Exemplo de uso
if __name__ == "__main__":
    destinatario = os.getenv("TEST_EMAIL_TO")
    assunto = "Teste de envio via classe Python"
    mensagem = "Este é um e-mail enviado por uma classe genérica em Python."

    sender = EmailSender()
    sender.send_email(destinatario, assunto, mensagem)
