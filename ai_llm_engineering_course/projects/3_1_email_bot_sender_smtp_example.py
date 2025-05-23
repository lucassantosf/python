import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

# Dados da sua conta Gmail
EMAIL = os.getenv("IMAP_MAIL")
SENHA = os.getenv("IMAP_PWD")

# Dados do e-mail
destinatario = os.getenv("TEST_EMAIL_TO")
assunto = "Teste de envio via Python"
mensagem = "Olá, este é um e-mail enviado via Python com Gmail SMTP!"

# Monta o e-mail
msg = MIMEMultipart()
msg["From"] = EMAIL
msg["To"] = destinatario
msg["Subject"] = assunto
msg.attach(MIMEText(mensagem, "plain"))

# Envia via SMTP do Gmail
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, SENHA)
        server.send_message(msg)
        print("✅ E-mail enviado com sucesso.")
except Exception as e:
    print("❌ Erro ao enviar e-mail:", e)