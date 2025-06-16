from utils.model import LLMModel                # Importando o modelo LLM
from utils.sender_smtp import EmailSender       # Importando EmailSender para enviar e-mails via smpt
from dotenv import load_dotenv
from utils.llm_utils import LLMUtils            # Importando utilitários para manipulação de LLM
import json
import os
import re                                       # Importando módulo de expressões regulares
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
            
            "REGRAS CRÍTICAS DE FORMATAÇÃO JSON:\n"
            "1. Use APENAS aspas duplas (\") para chaves e valores, NUNCA aspas simples (')\n"
            "2. Cada objeto DEVE terminar com vírgula (,) exceto o último\n"
            "3. NUNCA use ponto-e-vírgula (;) em nenhum lugar do JSON\n"
            "4. Não inclua caracteres especiais ou não-ASCII no JSON\n"
            "5. Certifique-se de que cada chave e valor estão corretamente entre aspas duplas\n"
            "6. Não use quebras de linha dentro dos valores de texto\n\n"
            
            "A resposta deve ser ESTRITAMENTE um array JSON puro. Não inclua nenhuma explicação, título, texto fora do JSON, markdown ou quebras de linha antes ou depois.\n"
            "Exemplo de resposta esperada:\n"
            "[\n"
            "  {\n"
            '    "title": "Erro ao salvar novo cachorro",\n'
            '    "description": "Tentei cadastrar um novo cachorro e apareceu uma mensagem de erro..."\n'
            "  },\n"
            "  {\n"
            '    "title": "Falha ao gerar relatório de pedigree",\n'
            '    "description": "Ao tentar gerar o relatório de pedigree do meu cachorro..."\n'
            "  },\n"
            "  ... (mais 8 objetos semelhantes) ...\n"
            "]"
        ) 

        messages = [
            {
                "role": "system",
                "content": "Você é um ESPECIALISTA em criar EXATAMENTE 10 simulações realistas de problemas técnicos em formato JSON. NUNCA use formatação markdown. SEMPRE retorne APENAS um array JSON válido, começando com '[' e terminando com ']'. Cada objeto no array deve ter exatamente duas propriedades: 'title' e 'description'. Não inclua nenhum texto fora do JSON. Não use cabeçalhos, negrito, itálico ou qualquer outra formatação. Apenas JSON puro."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_model.generate_completion(messages)
        
        # Imprimir os primeiros 200 caracteres da resposta para diagnóstico
        print(f"Primeiros 200 caracteres da resposta: {response[:200]}")
        
        # Abordagem direta: extrair apenas o que parece ser JSON
        json_start = response.find("[")
        json_end = response.rfind("]") + 1
        
        if json_start >= 0 and json_end > json_start:
            # Extrair o que parece ser JSON
            json_text = response[json_start:json_end]
            print(f"JSON extraído (primeiros 100 caracteres): {json_text[:100]}...")
            
            # Tentar corrigir problemas comuns
            json_text = json_text.replace(";", ",")
            json_text = json_text.replace("'", '"')
            
            # Abordagem extrema: extrair manualmente cada objeto e reconstruir o JSON
            try:
                print("Tentando extração manual de objetos...")
                # Extrair todos os objetos que começam com { e terminam com }
                objects = re.findall(r'{[^{}]*"title"[^{}]*"description"[^{}]*}', json_text, re.DOTALL)
                
                if objects:
                    print(f"Encontrados {len(objects)} objetos potenciais.")
                    valid_objects = []
                    
                    for i, obj_text in enumerate(objects):
                        # Limpar cada objeto individualmente
                        clean_obj = obj_text.replace(";", ",").replace("'", '"')
                        
                        # Garantir que todas as chaves estão entre aspas duplas
                        clean_obj = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', clean_obj)
                        
                        # Remover vírgulas extras antes de fechar chaves
                        clean_obj = re.sub(r',\s*}', '}', clean_obj)
                        
                        try:
                            # Tentar analisar o objeto
                            obj = json.loads(clean_obj)
                            
                            # Verificar se tem os campos necessários
                            if "title" in obj and "description" in obj:
                                valid_objects.append(obj)
                                print(f"Objeto {i+1} válido: {obj['title'][:30]}...")
                        except json.JSONDecodeError as e:
                            print(f"Objeto {i+1} inválido: {e}")
                    
                    if valid_objects:
                        print(f"Extração manual bem-sucedida! {len(valid_objects)} objetos válidos.")
                        return json.dumps(valid_objects)
            except Exception as e:
                print(f"Erro na extração manual: {e}")
            
            # Se a extração manual falhar, tentar analisar o JSON corrigido
            try:
                incidents = json.loads(json_text)
                print(f"JSON analisado com sucesso! Encontrados {len(incidents)} incidentes.")
                clean_response = json.dumps(incidents)
                return clean_response
            except json.JSONDecodeError as e:
                print(f"Erro ao analisar JSON extraído: {e}")
                
                # Tentar corrigir o erro específico
                if "Expecting ',' delimiter" in str(e):
                    error_match = re.search(r'line (\d+) column (\d+)', str(e))
                    if error_match:
                        error_line = int(error_match.group(1))
                        error_col = int(error_match.group(2))
                        
                        print(f"Tentando corrigir erro específico na linha {error_line}, coluna {error_col}...")
                        
                        # Dividir o texto em linhas
                        lines = json_text.split('\n')
                        
                        # Verificar se a linha de erro está dentro dos limites
                        if 0 < error_line <= len(lines):
                            # Ajustar para índice baseado em zero
                            line_idx = error_line - 1
                            problematic_line = lines[line_idx]
                            
                            print(f"Linha problemática: {problematic_line}")
                            
                            # Inserir uma vírgula na posição do erro
                            if error_col <= len(problematic_line):
                                fixed_line = problematic_line[:error_col] + ',' + problematic_line[error_col:]
                                lines[line_idx] = fixed_line
                                print(f"Linha corrigida: {fixed_line}")
                                
                                # Reconstruir o JSON
                                fixed_json = '\n'.join(lines)
                                
                                try:
                                    incidents = json.loads(fixed_json)
                                    print(f"JSON corrigido com sucesso! Encontrados {len(incidents)} incidentes.")
                                    return json.dumps(incidents)
                                except json.JSONDecodeError as e2:
                                    print(f"Ainda há erro após correção específica: {e2}")
                # Continuar com outras abordagens
        
        # Se a abordagem direta falhar, tentar métodos mais robustos
        try:
            # Tentar usar o método robusto de análise JSON
            incidents = self.robust_json_parse(response)
            print(f"JSON processado com sucesso! Encontrados {len(incidents)} incidentes.")
            clean_response = json.dumps(incidents)
            return clean_response
        except Exception as e:
            print(f"Erro na análise robusta: {e}")
            
            # Tentar extrair e limpar o JSON manualmente
            try:
                clean_response = self.extract_json_from_response(response)
                clean_response = self.clean_json_string(clean_response)
                
                # Verificar se o JSON é válido
                if self.is_valid_json(clean_response):
                    incidents = json.loads(clean_response)
                    print(f"JSON extraído e limpo com sucesso! Encontrados {len(incidents)} incidentes.")
                else:
                    # Tentar uma limpeza mais agressiva
                    clean_response = clean_response.replace(";", ",").replace("'", '"')
                    if self.is_valid_json(clean_response):
                        incidents = json.loads(clean_response)
                        print(f"JSON limpo agressivamente com sucesso! Encontrados {len(incidents)} incidentes.")
                    else:
                        # Tentar o método de emergência
                        try:
                            incidents = self.emergency_json_fix(clean_response)
                            if incidents:
                                clean_response = json.dumps(incidents)
                                print(f"Extração de emergência bem-sucedida! Encontrados {len(incidents)} incidentes.")
                            else:
                                # Última tentativa: construção manual de JSON
                                print("Tentando construção manual de JSON...")
                                incidents = self.manual_json_construction(response)
                                if incidents:
                                    clean_response = json.dumps(incidents)
                                    print(f"Construção manual bem-sucedida! Encontrados {len(incidents)} incidentes.")
                                    return clean_response
                                else:
                                    raise ValueError("Método de emergência falhou")
                        except Exception as ex:
                            print(f"Todas as tentativas de extração falharam: {ex}")
                            # Retornar um array vazio para indicar falha
                            return "[]"
            except Exception as e:
                print(f"Erro ao extrair JSON: {e}")
                return "[]"
        
        # Se chegamos aqui, temos um JSON válido em clean_response
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
                
                # Usar métodos robustos para analisar a resposta adicional
                try:
                    additional_incidents = self.robust_json_parse(additional_response)
                    print(f"JSON adicional processado com sucesso! Encontrados {len(additional_incidents)} incidentes adicionais.")
                    
                    # Garantir que não pegamos mais do que precisamos
                    additional_incidents = additional_incidents[:missing_count]
                    # Combinar os incidentes originais com os adicionais
                    incidents.extend(additional_incidents)
                    print(f"Agora temos {len(incidents)} incidentes no total.")
                    return json.dumps(incidents)
                except Exception as e:
                    print(f"Erro ao processar incidentes adicionais: {e}")
                    # Continuar com os incidentes que já temos
                    print("Continuando com os incidentes já gerados.")
            
            return clean_response
        except json.JSONDecodeError as e:
            print(f"Erro ao processar JSON: {e}")

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

def get_default_incidents():
    """
    Retorna uma lista de incidentes padrão para usar como fallback.
    """
    return [
        {
            "title": "Erro 404 ao tentar acessar relatórios de pedigree em dispositivos iOS",
            "description": "Estou tentando acessar os relatórios de pedigree do meu cachorro através do meu iPhone 13 com iOS 16.2, mas constantemente recebo um erro 404. Já tentei usar diferentes navegadores (Safari, Chrome e Firefox), limpar o cache e cookies, e até mesmo reinstalar os aplicativos, mas o problema persiste. Curiosamente, consigo acessar os relatórios normalmente através do meu laptop com Windows. Este problema está impedindo que eu verifique informações importantes sobre a linhagem do meu cachorro durante visitas a exposições caninas. A mensagem de erro exata é: 'Erro 404: Recurso não encontrado. O relatório solicitado não está disponível no momento.' Preciso urgentemente de uma solução, pois tenho uma exposição importante em três dias."
        },
        {
            "title": "Falha na sincronização de dados do cachorro com a pedigree em diferentes dispositivos",
            "description": "Atualizei as informações do meu cachorro (vacinas, peso, altura) no meu tablet Android (Samsung Galaxy Tab S7, Android 12), mas quando acesso o sistema pelo meu computador (Windows 11, Chrome 98.0.4758.102), as alterações não aparecem. Já tentei forçar a sincronização usando o botão 'Atualizar dados' na interface, limpei o cache do navegador, e até mesmo esperei 24 horas, mas as informações continuam desatualizadas. O console de desenvolvedor mostra o erro: 'SyncError: Failed to update record #45872 - Database conflict'. Este problema está afetando meu trabalho como criador, pois preciso ter acesso consistente aos dados atualizados em todos os dispositivos para gerenciar adequadamente meu canil."
        },
        {
            "title": "Incompatibilidade do sistema com navegador Firefox 98.2 ao fazer upload de fotos",
            "description": "Estou tentando fazer upload de fotos do meu cachorro usando o Firefox 98.2 no Windows 10, mas o sistema trava consistentemente após selecionar as imagens. O indicador de progresso chega a 45% e então congela, seguido por uma mensagem de erro: 'Falha no processamento de imagem: formato não suportado'. As mesmas imagens (JPG, 2MB cada) funcionam perfeitamente quando uso o Chrome. Já tentei desativar todas as extensões do Firefox, limpar o cache e até reinstalar o navegador, mas o problema persiste. Inspecionando o console, vejo o erro: 'Uncaught TypeError: Cannot read property 'processImage' of undefined'. Isso está atrasando a atualização do perfil dos meus cachorros para o próximo evento de exposição."
        },
        {
            "title": "Erro ao tentar gerar certificado de pedigree em formato PDF",
            "description": "Quando tento gerar o certificado de pedigree em PDF para meu cachorro recém-registrado, o sistema processa por aproximadamente 30 segundos e depois exibe a mensagem: 'Erro na geração do documento: Falha ao renderizar gráfico de linhagem'. Estou usando um MacBook Pro com macOS Monterey 12.3 e Safari 15.4. Já tentei usar o Chrome e o Firefox, mas o resultado é o mesmo. O problema ocorre especificamente com este cachorro; consigo gerar certificados para outros animais sem problemas. Analisando o histórico deste animal, notei que ele tem uma linhagem particularmente extensa (7 gerações completas), o que pode estar causando o problema. Preciso deste certificado para uma exposição internacional na próxima semana."
        },
        {
            "title": "Sistema trava ao tentar adicionar mais de 5 fotos simultaneamente na galeria do cachorro",
            "description": "Estou tentando adicionar 8 fotos de alta resolução (cada uma com aproximadamente 4MB, formato JPEG) simultaneamente na galeria do meu cachorro, mas o sistema trava completamente. O navegador (Chrome 99.0.4844.51 no Windows 11) fica sem responder por cerca de 2 minutos e depois exibe a mensagem: 'Esta página não está respondendo. Aguarde ou encerre o processo'. No console de desenvolvedor, vejo o erro: 'OutOfMemoryError: Allocation failed - JavaScript heap out of memory'. Se adiciono as fotos uma por uma, funciona, mas é extremamente ineficiente. Já tentei reduzir a resolução das imagens e usar diferentes navegadores, mas o problema persiste com múltiplos uploads."
        },
        {
            "title": "Falha ao exportar histórico médico do cachorro para formato CSV",
            "description": "Estou tentando exportar o histórico médico completo do meu cachorro para um arquivo CSV para compartilhar com o veterinário, mas o sistema gera um arquivo corrompido. Quando tento abrir o arquivo no Excel ou Google Sheets, recebo a mensagem: 'O arquivo está danificado e não pode ser aberto'. Analisando o arquivo gerado, percebi que ele contém caracteres estranhos no início (�PNG) e parece estar misturando formatos. Estou usando um Dell XPS 15 com Windows 10 Pro e Edge 99.0.1150.46. Já tentei diferentes navegadores e até mesmo acessar de outro computador, mas o problema persiste. O histórico deste cachorro é particularmente extenso, com 47 entradas médicas ao longo de 6 anos."
        },
        {
            "title": "Erro de validação ao tentar registrar cachorro com microchip já existente",
            "description": "Estou tentando registrar um novo cachorro no sistema, mas recebo o erro: 'Validação falhou: O número de microchip 900182000123456 já está registrado no sistema'. O problema é que este cachorro é meu e acabou de ser transferido para mim por outro criador que também usa o sistema. Já verifiquei com o criador anterior e ele confirmou que removeu o cachorro do sistema dele antes da transferência. Tentei contatar o suporte técnico, mas ainda não recebi resposta após 3 dias. Preciso registrar este animal urgentemente para participar de uma exposição na próxima semana. Estou usando um HP Pavilion com Windows 10 e Chrome 98.0.4758.102."
        },
        {
            "title": "Interface de usuário quebrada ao acessar o sistema em tela ultrawide (21:9)",
            "description": "Estou usando um monitor ultrawide LG 34WN750 com resolução 3440x1440 (proporção 21:9) e o layout da interface do sistema está completamente quebrado. Os elementos da página estão sobrepostos, alguns botões ficam inacessíveis e o menu lateral desaparece parcialmente sob outros elementos. Já tentei diferentes navegadores (Chrome, Firefox e Edge), ajustar o zoom da página e até mesmo mudar a resolução do monitor, mas o problema persiste. Curiosamente, quando conecto meu laptop a um monitor padrão 16:9, tudo funciona perfeitamente. Este problema está afetando significativamente minha produtividade, pois preciso alternar constantemente entre monitores para usar o sistema adequadamente."
        },
        {
            "title": "Sistema não calcula corretamente a idade do cachorro em exposições",
            "description": "Descobri que o sistema está calculando incorretamente a idade do meu cachorro para fins de categorização em exposições. Meu cachorro nasceu em 15/03/2020, mas o sistema está considerando-o como tendo 6 meses a menos do que realmente tem. Isso fez com que ele fosse inscrito na categoria errada em uma exposição recente, o que resultou em sua desclassificação. Analisando mais detalhadamente, percebi que o problema ocorre apenas com cachorros nascidos no primeiro trimestre de 2020. Estou usando um Lenovo ThinkPad com Windows 11 e Firefox 97.0.1. Já tentei atualizar os dados do cachorro e até mesmo excluí-lo e registrá-lo novamente, mas o cálculo continua incorreto."
        },
        {
            "title": "Falha ao tentar conectar conta do sistema com aplicativo móvel",
            "description": "Estou tentando conectar minha conta do sistema LIBERDADE ANIMAL com o aplicativo móvel (versão 2.3.5 no Android 12, Samsung Galaxy S22). Quando insiro minhas credenciais no aplicativo e clico em 'Conectar', recebo a mensagem: 'Falha na autenticação: Token inválido'. Já verifiquei que minhas credenciais estão corretas (consigo fazer login normalmente pelo navegador), reinstalei o aplicativo, limpei os dados do aplicativo e até mesmo resetei as configurações de rede do meu celular. No log de erros do aplicativo, vejo: 'OAuth2Error: Invalid grant_type parameter'. Este problema está impedindo que eu receba notificações importantes sobre meus cachorros e acesse informações quando estou em exposições sem acesso a um computador."
        }
    ]

def main():
    # Initialize models
    llm_model = LLMModel()
    seeder = IncidentSeeder(llm_model)
    sender = EmailSender(email=os.getenv("SEEDER_MAILER"), password=os.getenv("SEEDER_MAILER_PWD"))

    print("Iniciando o Seeder de Incidentes...")

    # Tentar gerar incidentes com o LLM
    try:
        incidents = seeder.generate_incidents()
        incidents_list = json.loads(incidents)
        
        # Verificar se temos incidentes válidos
        if not incidents_list:
            print("O LLM não gerou incidentes válidos. Usando incidentes padrão...")
            incidents_list = get_default_incidents()
    except Exception as e:
        print(f"Erro ao gerar incidentes com o LLM: {e}")
        print("Usando incidentes padrão...")
        incidents_list = get_default_incidents()
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
