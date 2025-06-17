from utils.model import LLMModel                # Importando o modelo LLM
from openai import OpenAI
from utils.reader import EmailReader
from utils.sender import EmailSender
from utils.llm_utils import LLMUtils            # Importando utilitários para manipulação de LLM
import json
import re                                       # Importando módulo de expressões regulares

class IncidentReplySeeder(LLMUtils):
    def __init__(self, llm_model):
        self.llm_model = llm_model

    def generate_replies_from_email_list(self, email_list):
        formatted_problems = ""
        for i, email in enumerate(email_list, start=1):
            formatted_problems += (
                f"{i}. ID: {email['message_id']}\n"
                f"De: {email['from']}, Assunto: {email['subject']}\n"
                f"Problema: {email['text']}\n\n"
            )

        # Criar um mapeamento de índices para message_ids para garantir correspondência exata
        email_mapping = {i+1: email for i, email in enumerate(email_list)}
        
        prompt = (
            f"Você é um assistente técnico ESPECIALISTA da plataforma web 'LIBERDADE ANIMAL'.\n"
            f"Recebeu os seguintes {len(email_list)} problemas reportados por diferentes usuários:\n\n"
            f"{formatted_problems}\n"
            f"IMPORTANTE: Você DEVE gerar EXATAMENTE {len(email_list)} respostas DIFERENTES e ÚNICAS, uma para CADA problema listado acima.\n"
            f"Para cada problema gere uma resposta DETALHADA, TÉCNICA e CRIATIVA com 100-150 palavras. Seja técnico mas também empático.\n\n"
            f"DIRETRIZES PARA RESPOSTAS:\n"
            f"- INVENTE detalhes técnicos específicos para cada problema (não use respostas genéricas)\n"
            f"- CRIE soluções técnicas diferentes para cada problema, mesmo que sejam similares\n"
            f"- MENCIONE ferramentas específicas como DevTools, Console de Depuração, Inspetor de Elementos, etc.\n"
            f"- SUGIRA configurações específicas para resolver o problema (ex: 'Desative a extensão X', 'Atualize para versão Y')\n"
            f"- INCLUA passos numerados e específicos para resolver o problema\n"
            f"- VARIE o formato e estrutura das respostas para que não sejam todas iguais\n"
            f"- PERSONALIZE cada resposta com base no problema específico\n\n"
            f"EXEMPLOS DE RESPOSTAS TÉCNICAS (apenas para referência, crie suas próprias respostas):\n\n"
            f"Exemplo 1: 'Identificamos que o erro 404 ao acessar relatórios no iOS está relacionado a um conflito entre o Safari 15.2 e nossa API REST. Recomendamos: 1) Limpe o cache do navegador em Configurações > Safari > Limpar Histórico; 2) Verifique se o iOS está atualizado para versão 15.4+; 3) Tente acessar usando o modo de navegação privada. Se o problema persistir, envie-nos capturas de tela do Console de Erros (abra Safari > Configurações > Avançado > Mostrar menu Desenvolvedor > Desenvolvedor > Console JavaScript).'\n\n"
            f"Exemplo 2: 'A incompatibilidade com o Chrome 98.1 durante uploads de fotos ocorre devido a uma limitação na API FileReader quando processamos imagens HEIC. Soluções: 1) Converta as imagens para JPG usando o aplicativo Fotos antes do upload; 2) Instale nossa extensão 'LIBERDADE ANIMAL Helper' disponível na Chrome Web Store; 3) Temporariamente, desative a aceleração de hardware em chrome://settings/system. Poderia nos enviar o log de erros (pressione F12 > Console) durante a tentativa de upload para diagnóstico adicional?'\n\n"
            f"Retorne os resultados em um ÚNICO JSON ARRAY SEM usar blocos de código (sem crases).\n\n"
            f"IMPORTANTE: \n"
            f"1. Você DEVE usar EXATAMENTE os mesmos valores de 'message_id', 'from' e 'subject' que foram fornecidos para cada problema.\n"
            f"2. NÃO altere ou invente novos valores para esses campos, pois isso causará falhas no sistema.\n"
            f"3. Sua resposta DEVE ser um ARRAY de objetos JSON, mesmo que seja apenas um único email.\n"
            f"4. Certifique-se de que sua resposta comece com '[' e termine com ']'.\n"
            f"5. CADA resposta deve ser ÚNICA e DIFERENTE das outras - isso é CRÍTICO para o treinamento do modelo.\n\n"
            f"""[
            {{
                "message_id": "id do email",
                "from": "email do remetente",
                "subject": "assunto do email",
                "problem": "resumo do problema",
                "solution": "resposta técnica detalhada e única para este problema específico"
            }},
            ...
            ]"""
                f"\nNão adicione nenhum outro conteúdo além do JSON descrito."
            )

        messages = [
            {
                "role": "system",
                "content": "Você é um especialista técnico ALTAMENTE QUALIFICADO que trabalha no suporte da plataforma 'LIBERDADE ANIMAL'. Você tem amplo conhecimento em desenvolvimento web, bancos de dados, redes, e sistemas operacionais. Suas respostas são DETALHADAS, TÉCNICAS e CRIATIVAS, sempre focadas em resolver problemas de forma eficiente. IMPORTANTE: Cada resposta que você gera DEVE ser ÚNICA e DIFERENTE das outras, com detalhes técnicos específicos e soluções personalizadas para cada problema. Você DEVE variar o formato, estrutura e conteúdo de suas respostas para que não sejam genéricas. Você DEVE incluir passos específicos, ferramentas de diagnóstico e configurações técnicas em suas respostas. Você DEVE inventar detalhes técnicos plausíveis quando necessário para criar respostas mais específicas e úteis."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_model.generate_completion(messages)
        return response

def main():
    # Usar o modelo OpenAI por padrão para melhor qualidade de respostas
    llm_model = LLMModel(use_openai=True)
    seeder = IncidentReplySeeder(llm_model)

    print("Lendo os e-mails não lidos...")
    reader = EmailReader()
    emails = reader.read_emails(max_results=10, query='is:unread')
    sender = EmailSender()

    print(f"Total de e-mails lidos: {len(emails)}")
    
    # Agrupar emails por thread_id para melhor visualização
    threads = {}
    for email in emails:
        thread_id = email['thread_id']
        if thread_id not in threads:
            threads[thread_id] = []
        threads[thread_id].append(email)
    
    print(f"\nTotal: {len(threads)} threads contendo {len(emails)} emails")
    
    # Limitar o número de emails processados se necessário
    max_emails_to_process = 10
    if len(emails) > max_emails_to_process:
        print(f"Limitando processamento aos primeiros {max_emails_to_process} emails...")
        emails = emails[:max_emails_to_process]

    if not emails:
        print("Nenhum email não lido encontrado. Encerrando.")
        return

    # Agrupar emails por assunto para evitar duplicatas
    emails_by_subject = {}
    for email in emails:
        subject = email['subject']
        if subject not in emails_by_subject:
            emails_by_subject[subject] = []
        emails_by_subject[subject].append(email)
    
    print("\n--- Emails agrupados por assunto ---")
    for subject, email_group in emails_by_subject.items():
        print(f"Assunto '{subject}': {len(email_group)} email(s)")
    print("--- Fim do agrupamento ---\n")
    
    # Manter um registro de quais assuntos já foram respondidos
    responded_subjects = set()
    
    # Processar cada assunto único
    print("Processando emails por assunto único...")
    for subject, email_group in emails_by_subject.items():
        # Pegar apenas o primeiro email de cada grupo com o mesmo assunto
        email = email_group[0]
        
        print(f"Gerando resposta personalizada para: {email['from']} - Assunto: {email['subject']}")
        
        # Gerar uma resposta personalizada usando o OpenAI
        single_email_prompt = (
            f"Você é um assistente técnico ESPECIALISTA da plataforma web 'LIBERDADE ANIMAL'.\n"
            f"Recebeu o seguinte problema reportado por um usuário:\n\n"
            f"De: {email['from']}, Assunto: {email['subject']}\n"
            f"Problema: {email['text']}\n\n"
            f"Gere uma resposta DETALHADA, TÉCNICA e CRIATIVA com 100-150 palavras. Seja técnico mas também empático.\n\n"
            f"DIRETRIZES PARA A RESPOSTA:\n"
            f"- INVENTE detalhes técnicos específicos para o problema\n"
            f"- CRIE uma solução técnica personalizada\n"
            f"- MENCIONE ferramentas específicas como DevTools, Console de Depuração, etc.\n"
            f"- SUGIRA configurações específicas para resolver o problema\n"
            f"- INCLUA passos numerados e específicos para resolver o problema\n\n"
            f"Retorne APENAS o texto da resposta, sem formatação adicional."
        )
        
        single_messages = [
            {"role": "system", "content": "Você é um especialista técnico que cria respostas detalhadas e personalizadas."},
            {"role": "user", "content": single_email_prompt}
        ]
        
        try:
            # Usar temperatura mais alta para respostas mais criativas
            custom_response = seeder.llm_model.generate_completion(single_messages, temperature=0.8)
            
            original_msg = {
                "from_": email['from'],
                "subject": email['subject'],
                "headers": {"Message-ID": email['message_id']},
                "thread_id": email['thread_id']
            }
            
            print(f"Enviando resposta para: {email['subject']}")
            result = sender.reply_email(
                original_msg=original_msg,
                reply_body=custom_response
            )
            
            if result:
                print("Resposta enviada com sucesso!")
                responded_subjects.add(subject)
            else:
                print("Tentativa de envio falhou.")
        except Exception as e:
            print(f"Erro ao processar email: {e}")

    print("\nProcessamento de emails concluído!")

if __name__ == "__main__":
    main()
