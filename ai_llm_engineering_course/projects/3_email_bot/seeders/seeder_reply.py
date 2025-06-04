from utils.model import LLMModel                # Importando o modelo LLM
from openai import OpenAI
from utils.reader import EmailReader
from utils.sender import EmailSender
from utils.llm_utils import LLMUtils            # Importando utilitários para manipulação de LLM
import json

class IncidentReplySeeder(LLMUtils):
    def __init__(self, llm_model):
        self.llm_model = llm_model

    def generate_replies_from_email_list(self, email_list):
        formatted_problems = ""
        for i, email in enumerate(email_list, start=1):
            formatted_problems += (
                f"{i}. De: {email['from']}, Assunto: {email['subject']}\n"
                f"Problema: {email['text']}\n\n"
            )

        prompt = (
            f"Você é um assistente técnico especialista da plataforma web 'LIBERDADE ANIMAL'.\n"
            f"Recebeu os seguintes problemas reportados por diferentes usuários:\n\n"
            f"{formatted_problems}\n"
            f"Para cada problema gere uma resposta diferente com 100 palavras. Seja técnico, solicitando prints ou anexos como evidência se necessário.\n"
            f"Retorne os resultados em um ÚNICO JSON SEM usar blocos de código (sem crases).:\n\n"
            f"""[
            {{
                "from": "email do remetente",
                "subject": "assunto do email",
                "problem": "problema original",
                "solution": "resposta técnica"
            }},
            ...
            ]"""
                f"\nNão adicione nenhum outro conteúdo além do JSON descrito."
            )

        messages = [
            {
                "role": "system",
                "content": "Você é um gerador de dados fictícios para simular respostas à incidentes de suporte técnico ocorridos no nosso sistema Web para Gerenciamento de Cachorros e Pedigrees 'LIBERDADE ANIMAL'"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_model.generate_completion(messages)
        return response

def main():
    llm_model = LLMModel()
    seeder = IncidentReplySeeder(llm_model)

    print("Lendo os e-mails ...")

    # Ler os e-mails
    reader = EmailReader(params={"seen": False})
    emails = reader.read_emails()
    sender = EmailSender()

    print(f"Total de e-mails lidos: {len(emails)}") 

    print("Gerando respostas para os e-mails...")

    response_text = seeder.generate_replies_from_email_list(emails)

    try:
        clean_json = seeder.extract_json_from_response(response_text)
        replies = json.loads(clean_json)
        print("Respostas geradas:", clean_json)
    except Exception as e:
        print("Erro ao converter resposta em JSON:", e)
        print("Resposta bruta:", response_text)
        return

    for reply in replies:

        print(f"Respondendo: {reply['from']} - Assunto: {reply['subject']}")

        # opcional: você pode usar um match pelos campos
        matching_email = next((e for e in emails if e['from'] == reply['from'] and e['subject'] == reply['subject']), None)
        if matching_email:
            sender.reply_email(
                original_msg=matching_email['raw'], 
                reply_body=reply['solution']
            )
            print("E-mail respondido com sucesso.")

if __name__ == "__main__":
    main()