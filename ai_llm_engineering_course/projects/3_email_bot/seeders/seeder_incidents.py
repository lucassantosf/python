from utils.model import LLMModel                # Importando o modelo LLM
from utils.sender_smtp import EmailSender       # Importando EmailSender para enviar e-mails via smpt
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
            "Gere uma lista com exatamente 10 incidentes técnicos DETALHADOS e REALISTAS relatados por usuários do nosso sistema web de gerenciamento de cachorros e pedigrees 'LIBERDADE ANIMAL'.\n\n"
            "DIRETRIZES PARA OS INCIDENTES:\n"
            "- Cada incidente deve ser ÚNICO e ESPECÍFICO\n"
            "- Inclua DETALHES TÉCNICOS como navegadores, versões, dispositivos específicos\n"
            "- Mencione FUNCIONALIDADES ESPECÍFICAS do sistema (cadastro de pedigree, upload de fotos, geração de relatórios, etc.)\n"
            "- Inclua PASSOS que o usuário tentou para resolver o problema\n"
            "- Descreva COMPORTAMENTOS ESPECÍFICOS do sistema (mensagens de erro exatas, comportamentos inesperados)\n"
            "- Use TERMINOLOGIA TÉCNICA apropriada\n"
            "- Inclua IMPACTO no trabalho do usuário\n\n"
            
            "Cada incidente deve conter APENAS:\n"
            "- Um título ESPECÍFICO, TÉCNICO e DETALHADO no campo 'title'\n"
            "- Uma descrição em primeira pessoa no campo 'description', com EXATAMENTE 200 palavras, rica em detalhes técnicos\n\n"
            
            "EXEMPLOS DE TÍTULOS BONS:\n"
            "- 'Erro 404 ao tentar acessar relatórios de pedigree em dispositivos iOS'\n"
            "- 'Falha na sincronização de dados do cachorro com a pedigree em diferentes dispositivos'\n"
            "- 'Incompatibilidade do sistema com navegador Firefox 98.2 ao fazer upload de fotos'\n\n"
            
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
                "content": "Você é um ESPECIALISTA em criar simulações realistas de problemas técnicos. Você tem profundo conhecimento em desenvolvimento web, UX/UI, bancos de dados, e sistemas operacionais. Você consegue criar cenários detalhados e tecnicamente precisos que simulam problemas reais que usuários enfrentam em sistemas web. Suas descrições são ricas em detalhes técnicos específicos, incluindo mensagens de erro exatas, comportamentos de sistema, e passos de reprodução claros. Você usa terminologia técnica apropriada e cria cenários que parecem ter sido escritos por usuários reais com problemas genuínos."
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
