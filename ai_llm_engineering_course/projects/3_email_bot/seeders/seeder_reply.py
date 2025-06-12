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
            f"IMPORTANTE: Você DEVE gerar EXATAMENTE {len(email_list)} respostas, uma para CADA problema listado acima.\n"
            f"Para cada problema gere uma resposta DETALHADA e CRIATIVA com EXATAMENTE 100 palavras. Seja técnico mas também empático.\n\n"
            f"DIRETRIZES PARA RESPOSTAS:\n"
            f"- Seja MUITO ESPECÍFICO e DETALHADO sobre possíveis causas do problema\n"
            f"- Sugira SOLUÇÕES TÉCNICAS CONCRETAS (mencione navegadores específicos, versões, configurações)\n"
            f"- Solicite PRINTS ou VÍDEOS específicos que ajudariam no diagnóstico\n"
            f"- Mencione FERRAMENTAS DE DIAGNÓSTICO específicas quando relevante\n"
            f"- Use LINGUAGEM TÉCNICA apropriada para demonstrar expertise\n"
            f"- Inclua PASSOS ESPECÍFICOS que o usuário deve seguir\n"
            f"- Seja EMPÁTICO mas PROFISSIONAL\n\n"
            f"Retorne os resultados em um ÚNICO JSON ARRAY SEM usar blocos de código (sem crases).\n\n"
            f"IMPORTANTE: \n"
            f"1. Você DEVE usar EXATAMENTE os mesmos valores de 'message_id', 'from' e 'subject' que foram fornecidos para cada problema.\n"
            f"2. NÃO altere ou invente novos valores para esses campos, pois isso causará falhas no sistema.\n"
            f"3. Sua resposta DEVE ser um ARRAY de objetos JSON, mesmo que seja apenas um único email.\n"
            f"4. Certifique-se de que sua resposta comece com '[' e termine com ']'.\n\n"
            f"""[
            {{
                "message_id": "id do email",
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
                "content": "Você é um especialista técnico ALTAMENTE QUALIFICADO que trabalha no suporte da plataforma 'LIBERDADE ANIMAL'. Você tem amplo conhecimento em desenvolvimento web, bancos de dados, redes, e sistemas operacionais. Suas respostas são DETALHADAS, TÉCNICAS e CRIATIVAS, sempre focadas em resolver problemas de forma eficiente. Você usa terminologia técnica apropriada e fornece instruções passo-a-passo claras. Você é capaz de diagnosticar problemas complexos com base em descrições limitadas e sugerir soluções específicas."
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

    reader = EmailReader()
    emails = reader.read_emails(max_results=10, query='is:unread')
    sender = EmailSender()

    print(f"Total de e-mails lidos: {len(emails)}")
    
    # Debugging: Explicação sobre o número de emails
    print("\n--- EXPLICAÇÃO SOBRE O NÚMERO DE EMAILS ---")
    print("O parâmetro max_results=10 limita o número de THREADS (conversas), não de emails individuais.")
    print("Cada thread pode conter múltiplos emails, por isso você pode receber mais emails do que o valor de max_results.")
    print("Veja abaixo a lista completa de emails recuperados, agrupados por thread_id:")
    
    # Agrupar emails por thread_id para melhor visualização
    threads = {}
    for email in emails:
        thread_id = email['thread_id']
        if thread_id not in threads:
            threads[thread_id] = []
        threads[thread_id].append(email)
    
    # Mostrar emails agrupados por thread
    for thread_num, (thread_id, thread_emails) in enumerate(threads.items(), 1):
        print(f"\nThread {thread_num} (ID: {thread_id}) - {len(thread_emails)} email(s):")
        for i, email in enumerate(thread_emails, 1):
            print(f"  Email {i}: De: {email['from']}, Assunto: {email['subject']}")
    
    print(f"\nTotal: {len(threads)} threads contendo {len(emails)} emails")
    print("--- Fim da explicação ---\n")
    
    # Opcionalmente, limitar o número de emails processados
    max_emails_to_process = 10  # Defina o número máximo de emails que você quer processar
    if len(emails) > max_emails_to_process:
        print(f"Limitando processamento aos primeiros {max_emails_to_process} emails...")
        emails = emails[:max_emails_to_process]

    print("Gerando respostas para os e-mails...")

    response_text = seeder.generate_replies_from_email_list(emails)

    try:
        # Tenta extrair o JSON da resposta
        try:
            clean_json = seeder.extract_json_from_response(response_text)
            replies = json.loads(clean_json)
        except ValueError as e:
            # Se falhar ao encontrar um array JSON, tenta tratar como um único objeto JSON
            print("Tentando processar como objeto JSON único...")
            # Verifica se a resposta parece ser um objeto JSON único
            if response_text.strip().startswith('{') and response_text.strip().endswith('}'):
                try:
                    # Tenta carregar diretamente como um objeto JSON
                    single_reply = json.loads(response_text)
                    # Converte para uma lista com um único item
                    replies = [single_reply]
                    print("Processado com sucesso como objeto JSON único.")
                except json.JSONDecodeError:
                    print("Erro ao converter resposta em JSON:", e)
                    print("Resposta bruta:", response_text)
                    return
            else:
                print("Erro ao converter resposta em JSON:", e)
                print("Resposta bruta:", response_text)
                return
        
        print("Respostas geradas:", json.dumps(replies, indent=4))
        
        # Verificar se o número de respostas corresponde ao número de emails
        if len(replies) != len(emails):
            print(f"AVISO: O modelo gerou {len(replies)} respostas para {len(emails)} emails.")
            
            # Se tiver mais respostas que emails, cortar o excesso
            if len(replies) > len(emails):
                print(f"Cortando para {len(emails)} respostas...")
                replies = replies[:len(emails)]
            
            # Se tiver menos respostas que emails, gerar respostas adicionais
            elif len(replies) < len(emails):
                print(f"Gerando {len(emails) - len(replies)} respostas adicionais...")
                
                # Mapear os emails que já têm respostas
                responded_email_ids = set(reply.get('message_id') for reply in replies)
                
                # Identificar emails sem resposta
                unreplied_emails = [email for email in emails if email['message_id'] not in responded_email_ids]
                
                # Gerar respostas adicionais para os emails sem resposta
                for email in unreplied_emails:
                    fallback_reply = {
                        "message_id": email['message_id'],
                        "from": email['from'],
                        "subject": email['subject'],
                        "problem": email['text'][:50] + "..." if len(email['text']) > 50 else email['text'],
                        "solution": (
                            f"Prezado(a) usuário,\n\n"
                            f"Agradecemos por entrar em contato com o suporte da plataforma LIBERDADE ANIMAL "
                            f"sobre o problema reportado: '{email['subject']}'.\n\n"
                            f"Estamos analisando sua solicitação e em breve entraremos em contato com mais informações. "
                            f"Para agilizar o processo, pedimos que nos envie capturas de tela ou qualquer informação adicional "
                            f"que possa nos ajudar a entender melhor o problema.\n\n"
                            f"Atenciosamente,\nEquipe de Suporte LIBERDADE ANIMAL"
                        )
                    }
                    replies.append(fallback_reply)
                
                print(f"Agora temos {len(replies)} respostas para {len(emails)} emails.")
    except Exception as e:
        print("Erro inesperado ao processar JSON:", e)
        print("Resposta bruta:", response_text)
        
        # Gerar respostas padrão para todos os emails em caso de falha completa
        print("Gerando respostas padrão para todos os emails...")
        replies = []
        for email in emails:
            fallback_reply = {
                "message_id": email['message_id'],
                "from": email['from'],
                "subject": email['subject'],
                "problem": email['text'][:50] + "..." if len(email['text']) > 50 else email['text'],
                "solution": (
                    f"Prezado(a) usuário,\n\n"
                    f"Agradecemos por entrar em contato com o suporte da plataforma LIBERDADE ANIMAL "
                    f"sobre o problema reportado: '{email['subject']}'.\n\n"
                    f"Estamos analisando sua solicitação e em breve entraremos em contato com mais informações. "
                    f"Para agilizar o processo, pedimos que nos envie capturas de tela ou qualquer informação adicional "
                    f"que possa nos ajudar a entender melhor o problema.\n\n"
                    f"Atenciosamente,\nEquipe de Suporte LIBERDADE ANIMAL"
                )
            }
            replies.append(fallback_reply)
        print(f"Geradas {len(replies)} respostas padrão.")

    # Manter um registro de quais emails foram respondidos (usando message_id como chave única)
    responded_emails = set()
    # Manter um registro de quais assuntos já foram respondidos
    responded_subjects = set()
    
    # Criar um mapeamento de emails por subject para evitar duplicatas
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
    
    # Processar as respostas geradas pelo LLM
    for reply in replies:
        # Verificar se já respondemos a um email com este assunto
        if reply['subject'] in responded_subjects:
            print(f"Pulando resposta para: {reply['from']} - Assunto: {reply['subject']} (assunto já respondido)")
            continue
            
        print(f"Preparando resposta para: {reply['from']} - Assunto: {reply['subject']}")

        # Primeiro tenta encontrar pelo message_id
        matching_email = next(
            (e for e in emails if e['message_id'] == reply['message_id']),
            None
        )

        # Se não encontrar pelo message_id, tenta encontrar pelo assunto e remetente
        if not matching_email:
            matching_email = next(
                (e for e in emails if e['subject'] == reply['subject'] and e['from'] == reply['from']),
                None
            )
            if matching_email:
                print(f"Email encontrado por assunto e remetente em vez de message_id")

        # Se ainda não encontrar, tenta buscar no Gmail diretamente
        if not matching_email:
            # Primeiro tenta pelo message_id
            matching_email = reader.find_email_by_message_id(reply['message_id'])
            
            # Se não encontrar, implementa uma busca por assunto
            if not matching_email:
                print(f"Tentando buscar email por assunto: {reply['subject']}")
                for email in emails:
                    if email['subject'] == reply['subject']:
                        matching_email = email
                        print(f"Email encontrado pelo assunto: {email['subject']}")
                        break

        if matching_email:
            # Marcar este email como respondido
            responded_emails.add(matching_email['message_id'])
            # Marcar este assunto como respondido
            responded_subjects.add(matching_email['subject'])
            
            original_msg = {
                "from_": matching_email['from'],
                "subject": matching_email['subject'],
                "headers": {"Message-ID": matching_email['message_id']},
                "thread_id": matching_email['thread_id']
            }

            print(f"Enviando resposta para: {original_msg}")
            try:
                result = sender.reply_email(
                    original_msg=original_msg,
                    reply_body=reply['solution']
                )

                if result:  # Aqui você pode verificar se o método te retorna algo
                    print("E-mail respondido com sucesso.")
                else:
                    print("Tentativa de envio falhou ou não retornou confirmação.")
            except Exception as e:
                print(f"Erro ao enviar resposta para {reply['from']}: {e}")
        else:
            print(f"Nenhum e-mail correspondente encontrado para message_id: {reply['message_id']}")

    # Verificar se há emails que não foram respondidos
    unreplied_emails = [email for email in emails if email['message_id'] not in responded_emails]
    
    if unreplied_emails:
        print(f"\n--- ATENÇÃO: {len(unreplied_emails)} emails não foram respondidos ---")
        print("Gerando respostas padrão para estes emails...")
        
        # Agrupar emails não respondidos por assunto para evitar responder múltiplos emails com o mesmo assunto
        unreplied_by_subject = {}
        for email in unreplied_emails:
            subject = email['subject']
            if subject not in unreplied_by_subject:
                unreplied_by_subject[subject] = []
            unreplied_by_subject[subject].append(email)
        
        # Gerar uma resposta padrão para apenas um email de cada assunto
        # Não resetamos responded_subjects aqui para evitar responder a assuntos já respondidos
        for subject, email_group in unreplied_by_subject.items():
            if subject in responded_subjects:
                continue
                
            # Pegar apenas o primeiro email de cada grupo com o mesmo assunto
            email = email_group[0]
            responded_subjects.add(subject)
            
            print(f"Gerando resposta padrão para: {email['from']} - Assunto: {email['subject']} (1 de {len(email_group)} com este assunto)")
            
            # Criar uma mensagem de resposta padrão
            fallback_response = (
                f"Prezado(a) usuário,\n\n"
                f"Agradecemos por entrar em contato com o suporte da plataforma LIBERDADE ANIMAL "
                f"sobre o problema reportado: '{email['subject']}'.\n\n"
                f"Estamos analisando sua solicitação e em breve entraremos em contato com mais informações. "
                f"Para agilizar o processo, pedimos que nos envie capturas de tela ou qualquer informação adicional "
                f"que possa nos ajudar a entender melhor o problema.\n\n"
                f"Atenciosamente,\nEquipe de Suporte LIBERDADE ANIMAL"
            )
            
            original_msg = {
                "from_": email['from'],
                "subject": email['subject'],
                "headers": {"Message-ID": email['message_id']},
                "thread_id": email['thread_id']
            }
            
            try:
                result = sender.reply_email(
                    original_msg=original_msg,
                    reply_body=fallback_response
                )
                
                if result:
                    print("Resposta padrão enviada com sucesso.")
                else:
                    print("Tentativa de envio da resposta padrão falhou.")
            except Exception as e:
                print(f"Erro ao enviar resposta padrão para {email['from']}: {e}")
    
    print("\nProcessamento de emails concluído!")

if __name__ == "__main__":
    main()
