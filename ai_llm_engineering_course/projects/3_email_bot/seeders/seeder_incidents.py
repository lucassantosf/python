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
            "Gere uma lista com EXATAMENTE 10 incidentes técnicos DETALHADOS e REALISTAS relatados por usuários do nosso sistema web de gerenciamento de cachorros e pedigrees 'LIBERDADE ANIMAL'.\n\n"
            "IMPORTANTE: Sua resposta DEVE conter EXATAMENTE 10 incidentes, nem mais nem menos.\n\n"
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
                "content": "Você é um ESPECIALISTA em criar EXATAMENTE 10 simulações realistas de problemas técnicos. Você tem profundo conhecimento em desenvolvimento web, UX/UI, bancos de dados, e sistemas operacionais. Você consegue criar cenários detalhados e tecnicamente precisos que simulam problemas reais que usuários enfrentam em sistemas web. Suas descrições são ricas em detalhes técnicos específicos, incluindo mensagens de erro exatas, comportamentos de sistema, e passos de reprodução claros. Você usa terminologia técnica apropriada e cria cenários que parecem ter sido escritos por usuários reais com problemas genuínos. SEMPRE gere EXATAMENTE 10 incidentes, nem mais nem menos."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_model.generate_completion(messages)
        clean_response = self.extract_json(response)

        # Se for válido, valida o número de incidentes
        if self.is_valid_json(clean_response):
            try:
                incidents = json.loads(clean_response)
                # Garantir que temos exatamente 10 incidentes
                if len(incidents) > 10:
                    print(f"O modelo gerou {len(incidents)} incidentes. Limitando para 10...")
                    incidents = incidents[:10]
                    return json.dumps(incidents)
                elif len(incidents) < 10:
                    print(f"O modelo gerou apenas {len(incidents)} incidentes em vez de 10. Gerando os {10 - len(incidents)} restantes...")
                    
                    # Gerar os incidentes faltantes
                    missing_count = 10 - len(incidents)
                    additional_prompt = (
                        f"Gere EXATAMENTE {missing_count} incidentes técnicos ADICIONAIS e DIFERENTES dos seguintes que já foram gerados:\n\n"
                        f"{json.dumps(incidents, indent=2)}\n\n"
                        f"Os novos incidentes devem seguir o mesmo formato, mas ser completamente diferentes em conteúdo.\n"
                        f"Retorne apenas um array JSON com os {missing_count} NOVOS incidentes, sem incluir os anteriores.\n"
                        f"Cada incidente deve ter um título técnico específico e uma descrição detalhada em primeira pessoa."
                    )
                    
                    additional_messages = [
                        {
                            "role": "system",
                            "content": "Você é um ESPECIALISTA em criar simulações realistas de problemas técnicos. Gere exatamente o número solicitado de incidentes, nem mais nem menos."
                        },
                        {
                            "role": "user",
                            "content": additional_prompt
                        }
                    ]
                    
                    additional_response = self.llm_model.generate_completion(additional_messages)
                    additional_clean = self.extract_json(additional_response)
                    
                    if self.is_valid_json(additional_clean):
                        try:
                            additional_incidents = json.loads(additional_clean)
                            # Garantir que não pegamos mais do que precisamos
                            additional_incidents = additional_incidents[:missing_count]
                            # Combinar os incidentes originais com os adicionais
                            incidents.extend(additional_incidents)
                            print(f"Agora temos {len(incidents)} incidentes no total.")
                            return json.dumps(incidents)
                        except json.JSONDecodeError:
                            print("Erro ao decodificar os incidentes adicionais.")
                    else:
                        print("Não foi possível gerar incidentes adicionais válidos.")
                
                return clean_response
            except json.JSONDecodeError:
                # Se falhar ao decodificar, continua com a correção
                pass

        # Tentar pedir correção ao modelo
        correction_prompt = (
            "Corrija o conteúdo abaixo para que ele seja um array JSON válido, contendo EXATAMENTE 10 objetos com as chaves 'title' e 'description'.\n"
            "Remova qualquer texto fora do JSON, e devolva apenas o JSON com EXATAMENTE 10 itens:\n\n"
            f"{response}"
        )
        correction_messages = [{"role": "user", "content": correction_prompt}]
        corrected = self.llm_model.generate_completion(correction_messages)
        clean_corrected = self.extract_json(corrected)

        if self.is_valid_json(clean_corrected):
            # Verificar novamente o número de incidentes após a correção
            try:
                incidents = json.loads(clean_corrected)
                if len(incidents) > 10:
                    print(f"Após correção, o modelo ainda gerou {len(incidents)} incidentes. Limitando para 10...")
                    incidents = incidents[:10]
                    return json.dumps(incidents)
            except json.JSONDecodeError:
                pass
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
        
        # Validação: garantir que temos exatamente 10 incidentes
        if len(incidents_list) != 10:
            print(f"AVISO: O modelo gerou {len(incidents_list)} incidentes em vez de 10.")
            # Se tiver mais de 10, corta para ficar com apenas 10
            if len(incidents_list) > 10:
                print(f"Cortando para 10 incidentes...")
                incidents_list = incidents_list[:10]
            # Se tiver menos de 10, gerar incidentes padrão para completar
            else:
                missing = 10 - len(incidents_list)
                print(f"Gerando {missing} incidentes padrão para completar o total de 10...")
                
                # Títulos e descrições padrão para completar se necessário
                default_incidents = [
                    {
                        "title": f"Erro técnico #{i+1} no sistema LIBERDADE ANIMAL",
                        "description": f"Estou enfrentando um problema técnico ao utilizar o sistema LIBERDADE ANIMAL. Quando tento acessar a funcionalidade principal, recebo uma mensagem de erro que impede o uso normal da plataforma. Já tentei atualizar a página, limpar o cache do navegador e até mesmo usar um navegador diferente, mas o problema persiste. Este erro está afetando minha produtividade e preciso de uma solução urgente para continuar meu trabalho. Por favor, ajudem a resolver este problema o mais rápido possível. Agradeço antecipadamente pela atenção e suporte."
                    } for i in range(missing)
                ]
                
                incidents_list.extend(default_incidents)
                print(f"Agora temos exatamente 10 incidentes para processar.")
        
        print(f"Processando {len(incidents_list)} incidentes...")
        
        for i, incident in enumerate(incidents_list):
            sender.send_email(
                to_address=os.getenv("SEEDER_INCIDENTS_RECEIVER_EMAIL"),
                subject=incident['title'],
                body=incident['description']
            )
            print(f"E-mail {i + 1} enviado com sucesso.")
    except json.JSONDecodeError as e:
        print("Erro ao converter para JSON:", e)
        print("Conteúdo retornado:", incidents)
        
        # Gerar 10 incidentes padrão como fallback
        print("Gerando 10 incidentes padrão como fallback...")
        incidents_list = [
            {
                "title": f"Erro técnico #{i+1} no sistema LIBERDADE ANIMAL",
                "description": f"Estou enfrentando um problema técnico ao utilizar o sistema LIBERDADE ANIMAL. Quando tento acessar a funcionalidade principal, recebo uma mensagem de erro que impede o uso normal da plataforma. Já tentei atualizar a página, limpar o cache do navegador e até mesmo usar um navegador diferente, mas o problema persiste. Este erro está afetando minha produtividade e preciso de uma solução urgente para continuar meu trabalho. Por favor, ajudem a resolver este problema o mais rápido possível. Agradeço antecipadamente pela atenção e suporte."
            } for i in range(10)
        ]
        
        print("Processando 10 incidentes padrão...")
        
        for i, incident in enumerate(incidents_list):
            try:
                sender.send_email(
                    to_address=os.getenv("SEEDER_INCIDENTS_RECEIVER_EMAIL"),
                    subject=incident['title'],
                    body=incident['description']
                )
                print(f"E-mail {i + 1} enviado com sucesso.")
            except Exception as e:
                print(f"Erro ao enviar e-mail {i + 1}: {e}")
        
        print("Processamento de incidentes padrão concluído.")
        return

    print("Seeder de Incidentes concluído.")

if __name__ == "__main__":
    main()
