from utils.model import LLMModel                # Importando o modelo LLM
from utils.sender import EmailSender            # Importando EmailSender para enviar e-mails
from dotenv import load_dotenv
from utils.llm_utils import LLMUtils            # Importando utilitários para manipulação de LLM
import json
import os
load_dotenv()

class IncidentSeeder(LLMUtils):
    def __init__(self, llm_model):
        self.llm_model = llm_model

    def generate_incidents(self):
        prompt = (
            "Gere uma lista com exatamente 10 incidentes técnicos fictícios relatados por usuários do nosso sistema web de gerenciamento de cachorros e pedigrees.\n"
            "Cada incidente deve conter APENAS:\n"
            "- Um título curto, direto e realista no campo 'title'\n"
            "- Uma descrição em primeira pessoa no campo 'description', com aproximadamente 200 palavras\n"
            "A resposta deve ser ESTRITAMENTE um array JSON puro. Não inclua nenhuma explicação, título, texto fora do JSON, markdown ou quebras de linha antes ou depois.\n"
            "Exemplo de resposta esperada:\n"
            "[\n"
            "  {\n"
            '    "title": "Erro ao salvar novo cachorro",\n'
            '    "description": "Tentei cadastrar um novo cachorro e apareceu uma mensagem de erro..."\n'
            "  },\n"
            "  ... (mais 9 objetos semelhantes) ...\n"
            "]"
        ) 

        messages = [
            {
                "role": "system",
                "content": "Você é um gerador de dados fictícios para simular incidentes de suporte técnico ocorridos no nosso sistema Web para Gerenciamento de Cachorros e Pedigrees 'LIBERDADE ANIMAL'.",
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_model.generate_completion(messages)
        clean_response = self.extract_json(response)

        # Se for válido, retorna
        if self.is_valid_json(clean_response):
            return clean_response

        # Tentar pedir correção ao modelo
        correction_prompt = (
            "Corrija o conteúdo abaixo para que ele seja um array JSON válido, contendo apenas objetos com as chaves 'title' e 'description'.\n"
            "Remova qualquer texto fora do JSON, e devolva apenas o JSON:\n\n"
            f"{response}"
        )
        correction_messages = [{"role": "user", "content": correction_prompt}]
        corrected = self.llm_model.generate_completion(correction_messages)
        clean_corrected = self.extract_json(corrected)

        if self.is_valid_json(clean_corrected):
            return clean_corrected
        else:
            print("Erro: O modelo não conseguiu gerar um JSON válido mesmo após a correção.")
            return "[]  # Falha ao gerar JSON válido mesmo após correção"

def main():
    # Initialize models
    llm_model = LLMModel()
    seeder = IncidentSeeder(llm_model)
    sender = EmailSender(email=os.getenv("SEEDER_MAILER"), password=os.getenv("SEEDER_MAILER_PWD"))

    print("Iniciando o Seeder de Incidentes...")

    # Generate incidents
    incidents = seeder.generate_incidents()
    try:
        incidents_list = json.loads(incidents)
        for i,incident in enumerate(incidents_list):
            sender.send_email(
                to_address=os.getenv("SEEDER_INCIDENTS_RECEIVER_EMAIL"),
                subject=incident['title'],
                body=incident['description']
            )
            print(F"E-mail {i + 1} enviado com sucesso.")
    except json.JSONDecodeError as e:
        print("Erro ao converter para JSON:", e)
        print("Conteúdo retornado:", incidents)

    print("Seeder de Incidentes concluído.")

if __name__ == "__main__":
    main()