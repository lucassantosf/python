from utils.model import LLMModel                # Importando o modelo LLM
from openai import OpenAI
from reader import EmailReader
from sender import EmailSender

class IncidentReplySeeder:
    def __init__(self, llm_model):
        self.llm_model = llm_model

    def generate_incident_reply_from_problem(self, base_problem):
        prompt = (
            f"Considere o seguinte problema relatado por um usuário da nossa plataforma web: '{base_problem}'.\n"
            f"Crie uma única resposta como se fosse de um técnico especialista respondendo esse problema.\n"
            f"A resposta deve conter:\n"
            f"- Um campo 'solution' com a proposta de solução em até 200 palavras, sendo proativo e pedindo evidencias do problema (print, anexo, etc) se necessário\n"
            f"Retorne SOMENTE o JSON com apenas a propriedade solution, sem formatação em Markdown\n"
            f"Formato de exemplo:\n"
            f"""[
                {{
                    "solution": "Crie a solução técnica aqui, pedindo evidências se necessário."
                }}
            ]"""
        ) 

        messages = [
            {
                "role": "system",
                "content": "Você é um gerador de dados fictícios para simular respostas à incidentes de suporte técnico com base em problemas reais do nosso sistema Web.",
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

    # Ler os e-mails não lidos
    reader = EmailReader(params={"seen": False})
    emails = reader.read_emails()
    sender = EmailSender()

    print(f"Total de e-mails lidos: {len(emails)}") 

    for email in emails:
        print(f"Lendo e-mail de {email['from']} com assunto '{email['subject']}'")
        print(f"Texto: {email['text']}")
        print("---")

        problem = email['text']   
        reply = seeder.generate_incident_reply_from_problem(base_problem=problem)
        print(reply)

        sender.reply_email(original_msg=email['raw'], reply_body=reply)
        print("E-mail respondido com sucesso.") 

if __name__ == "__main__":
    main()
