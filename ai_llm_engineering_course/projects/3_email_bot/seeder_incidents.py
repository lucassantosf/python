from openai import OpenAI
from sender import EmailSender # Importando EmailSender para enviar e-mails
from dotenv import load_dotenv
import json
import re
import os
load_dotenv()

class IncidentSeeder:
    def __init__(self, llm_model):
        self.llm_model = llm_model

    def generate_incidents(self):
        prompt = (
            f"Gere uma lista com 10 incidentes técnicos relatados por usuários "
            f"de um sistema web fictício. Cada incidente deve conter:\n"
            f"- Um título curto\n"
            f"- Uma descrição do problema (em primeira pessoa, como se o usuário estivesse relatando)\n"
            f"Retorne SOMENTE um array JSON puro, sem explicações, sem markdown, sem texto adicional. Exemplo de saída válida:"
            f"""[
            {{
                "title": "Erro ao gerar relatório",
                "description": "Quando tento gerar o relatório de vendas, o sistema trava e não responde.",
            }}
            ]"""
        )

        messages = [
            {
                "role": "system",
                "content": "Você é um gerador de dados fictícios para simular incidentes de suporte técnico.",
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_model.generate_completion(messages)
        return response

class LLMModel:
    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:11434/v1",api_key="ollama")
        self.model_name = "llama3.2:1b"

    def generate_completion(self,messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0
            )
            return response.choices[0].message.content 
        except Exception as e:
            return f"Error generating response: {str(e)}" 

def main():
    # Initialize models
    llm_model = LLMModel()
    seeder = IncidentSeeder(llm_model)
    sender = EmailSender()

    # Generate incidents
    incidents = seeder.generate_incidents()
    try:
        incidents_list = json.loads(incidents)
        for incident in incidents_list:
            sender.send_email(
                to_address=os.getenv("IMAP_MAIL"),
                subject=incident['title'],
                body=incident['description']
            )
            print("E-mail enviado com sucesso.")
    except json.JSONDecodeError as e:
        print("Erro ao converter para JSON:", e)
        print("Conteúdo retornado:", incidents)

if __name__ == "__main__":
    main()