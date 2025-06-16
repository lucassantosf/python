from openai import OpenAI
from utils.reader import EmailReader
from utils.sender import EmailSender
from utils.model import LLMModel
from chromadb.utils import embedding_functions
import chromadb
import json
import os

def main():
    """
    Função principal que processa emails não lidos, busca perguntas similares na base de conhecimento,
    encontra respostas associadas e envia como resposta ao email original.
    """
    reader = EmailReader()
    sender = EmailSender()
    
    # Ler emails não lidos
    emails = reader.read_emails(max_results=1, query='is:unread')
    print(f"Encontrados {len(emails)} novos emails para processar.")
    
    if not emails:
        print("Nenhum email novo para processar.")
        return
    
    # Configurar ChromaDB
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    try:
        # Garantir que o diretório existe
        os.makedirs("./db/chroma_persist", exist_ok=True)
        chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
        collection = chromadb_client.get_or_create_collection("email_bot", embedding_function=default_ef)
    except Exception as e:
        print(f"Erro ao conectar com o ChromaDB: {e}")
        print("Verifique se a base de dados foi criada executando o script indexer.py primeiro.")
        return
    
    # Verificar se há documentos na coleção
    try:
        collection_info = collection.get(limit=1)
        if not collection_info["ids"]:
            print("A coleção está vazia. Execute o script indexer.py para indexar emails primeiro.")
            return
    except Exception as e:
        print(f"Erro ao verificar a coleção: {e}")
        return
    
    # Processar cada email
    for i, email in enumerate(emails, 1):
        print(f"\n[{i}/{len(emails)}] Processando email de {email['from']} - Assunto: {email['subject']}")
        
        # Preparar o texto da consulta - usar apenas as primeiras 1000 caracteres para evitar ruído
        query_text = email['text'][:1000] if len(email['text']) > 1000 else email['text']
        
        print(f"\nTexto da consulta: {query_text[:100]}...")
        
        # Busca semântica por perguntas similares
        try:
            # Primeiro, buscar todas as perguntas disponíveis para análise
            all_questions = collection.get(
                where={"$and": [
                    {"type": {"$eq": "pergunta"}},
                    {"has_response": {"$eq": True}}
                ]},
                include=["metadatas"]
            )
            
            print(f"Total de perguntas disponíveis com resposta: {len(all_questions['ids'])}")
            
            # Busca semântica com mais resultados para ter mais opções
            results = collection.query(
                query_texts=[query_text],
                n_results=min(5, len(all_questions['ids'])),  # Buscar mais resultados, mas não mais que o total disponível
                where={"$and": [
                    {"type": {"$eq": "pergunta"}},
                    {"has_response": {"$eq": True}}
                ]}  # Garantir que só buscamos perguntas com resposta
            )
            
            if not results["ids"] or len(results["ids"][0]) == 0:
                print("Nenhuma pergunta similar encontrada na base de conhecimento.")
                continue
                
            # Definir um limiar de similaridade (quanto menor o valor, mais similar)
            # ChromaDB usa distância, então valores menores são melhores
            similarity_threshold = 1.5  # Ajuste este valor conforme necessário
            
            # Filtrar resultados por similaridade
            filtered_results = {
                "ids": [],
                "documents": [],
                "metadatas": [],
                "distances": []
            }
            
            for i, distance in enumerate(results["distances"][0]):
                if distance < similarity_threshold:
                    filtered_results["ids"].append(results["ids"][0][i])
                    filtered_results["documents"].append(results["documents"][0][i])
                    filtered_results["metadatas"].append(results["metadatas"][0][i])
                    filtered_results["distances"].append(distance)
            
            if not filtered_results["ids"]:
                print(f"Nenhuma pergunta com similaridade suficiente encontrada (limiar: {similarity_threshold}).")
                continue
                
            print(f"Encontradas {len(filtered_results['ids'])} perguntas com similaridade suficiente.")
                
            # Mostrar as perguntas encontradas com suas pontuações de similaridade
            print("\n=== PERGUNTAS SIMILARES ENCONTRADAS ===")
            for j, (pergunta_id, pergunta_doc, pergunta_meta, distance) in enumerate(
                zip(filtered_results["ids"], filtered_results["documents"], 
                    filtered_results["metadatas"], filtered_results["distances"]), 1
            ):
                print(f"\n{j}) Pergunta: {pergunta_meta.get('subject')}")
                print(f"   Similaridade: {distance}")
                print(f"   ID: {pergunta_id}")
                print(f"   Thread ID: {pergunta_meta.get('thread_id')}")
                print(f"   Tem resposta: {pergunta_meta.get('has_response', False)}")
                
                # Se a pergunta tem uma resposta associada, buscar e mostrar
                if pergunta_meta.get("has_response") and pergunta_meta.get("response_id"):
                    response_id = pergunta_meta.get("response_id")
                    
                    # Buscar a resposta pelo ID
                    response_results = collection.get(
                        ids=[response_id],
                        include=["documents", "metadatas"]
                    )
                    
                    if response_results["ids"]:
                        resp_doc = response_results["documents"][0]
                        resp_meta = response_results["metadatas"][0]
                        
                        print(f"\n   RESPOSTA ASSOCIADA:")
                        print(f"   De: {resp_meta.get('from')}")
                        print(f"   Assunto: {resp_meta.get('subject')}")
                        print(f"   Texto da resposta:\n{resp_doc[:200]}...")
                        
                        # Se for a primeira pergunta (mais similar), enviar a resposta automaticamente
                        if j == 1:
                            print("\n=== ENVIANDO RESPOSTA AUTOMATICAMENTE ===")
                            
                            # Preparar o email original para resposta
                            original_msg = {
                                "from_": email['from'],
                                "subject": email['subject'],
                                "headers": {"Message-ID": email['message_id']},
                                "thread_id": email['thread_id']
                            }
                            
                            # Enviar a resposta
                            try:
                                result = sender.reply_email(
                                    original_msg=original_msg,
                                    reply_body=resp_doc
                                )
                                
                                if result:
                                    print(f"✅ Resposta enviada com sucesso para {email['from']}!")
                                else:
                                    print(f"❌ Falha ao enviar resposta para {email['from']}.")
                            except Exception as e:
                                print(f"❌ Erro ao enviar resposta: {e}")
                    else:
                        print(f"Resposta referenciada (ID: {response_id}) não encontrada!")
                else:
                    print("Esta pergunta não tem resposta associada.")
            
        except Exception as e:
            print(f"Erro ao buscar perguntas similares: {e}")
    
    print("\nProcessamento de emails concluído!")

def debug_collection():
    """
    Função para depurar a coleção do ChromaDB, mostrando informações sobre os documentos armazenados.
    """
    try:
        # Configurar ChromaDB
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
        collection = chromadb_client.get_or_create_collection("email_bot", embedding_function=default_ef)
        
        # Buscar todos os documentos
        results = collection.get(include=["documents", "metadatas"])
        
        # Contar perguntas e respostas
        perguntas = [meta for meta in results["metadatas"] if meta.get("type") == "pergunta"]
        respostas = [meta for meta in results["metadatas"] if meta.get("type") == "resposta"]
        perguntas_com_resposta = [p for p in perguntas if p.get("has_response") == True]
        
        print(f"\n=== RESUMO DA COLEÇÃO ===")
        print(f"Total de documentos: {len(results['ids'])}")
        print(f"Perguntas: {len(perguntas)}")
        print(f"Respostas: {len(respostas)}")
        print(f"Perguntas com resposta: {len(perguntas_com_resposta)}")
        
        # Verificar se há discrepâncias
        if len(perguntas_com_resposta) != len(respostas):
            print(f"\n⚠️ ALERTA: Há uma discrepância entre perguntas com resposta ({len(perguntas_com_resposta)}) e respostas ({len(respostas)})!")
        
        # Mostrar todas as respostas disponíveis
        print("\n=== TODAS AS RESPOSTAS DISPONÍVEIS ===")
        for i, meta in enumerate(results["metadatas"]):
            if meta.get("type") == "resposta":
                print(f"\n{i+1}) ID: {results['ids'][i]}")
                print(f"   De: {meta.get('from', 'Desconhecido')}")
                print(f"   Assunto: {meta.get('subject', 'Sem assunto')}")
                print(f"   Thread ID: {meta.get('thread_id', 'Desconhecido')}")
                print(f"   Em resposta a: {meta.get('in_reply_to', 'Desconhecido')}")
                print(f"   Texto: {results['documents'][i][:100]}...")
        
        # Mostrar todos os pares pergunta-resposta
        print("\n=== TODOS OS PARES PERGUNTA-RESPOSTA ===")
        for i, meta in enumerate(results["metadatas"]):
            if meta.get("type") == "pergunta" and meta.get("has_response") == True:
                print(f"\nPergunta: {meta.get('subject')}")
                print(f"ID: {results['ids'][i]}")
                print(f"Thread ID: {meta.get('thread_id')}")
                print(f"Response ID: {meta.get('response_id')}")
                print(f"Texto: {results['documents'][i][:100]}...")
                
                # Buscar a resposta
                response_id = meta.get("response_id")
                if response_id:
                    for j, id_ in enumerate(results["ids"]):
                        if id_ == response_id:
                            resp_meta = results["metadatas"][j]
                            resp_doc = results["documents"][j]
                            print(f"\nResposta correspondente:")
                            print(f"De: {resp_meta.get('from')}")
                            print(f"Texto: {resp_doc[:150]}...")
                            break
                    else:
                        print("\n⚠️ Resposta referenciada mas não encontrada!")
                        
                        # Tentar encontrar por thread_id
                        thread_id = meta.get("thread_id")
                        expected_response_id = f"{thread_id}-resposta"
                        print(f"Procurando por ID alternativo: {expected_response_id}")
                        
                        for j, id_ in enumerate(results["ids"]):
                            if id_ == expected_response_id:
                                resp_meta = results["metadatas"][j]
                                resp_doc = results["documents"][j]
                                print(f"\nResposta encontrada com ID alternativo:")
                                print(f"De: {resp_meta.get('from')}")
                                print(f"Texto: {resp_doc[:150]}...")
                                print(f"\n⚠️ Problema detectado: A pergunta referencia '{response_id}' mas a resposta tem ID '{expected_response_id}'")
                                break
                
                print("-" * 60)
        
        # Mostrar estatísticas de similaridade entre perguntas
        if len(perguntas) > 1:
            print("\n=== TESTE DE SIMILARIDADE ENTRE PERGUNTAS ===")
            print("Testando similaridade entre as perguntas para verificar se há duplicatas semânticas...")
            
            # Pegar apenas os textos das perguntas
            pergunta_texts = []
            pergunta_ids = []
            for i, meta in enumerate(results["metadatas"]):
                if meta.get("type") == "pergunta":
                    pergunta_texts.append(results["documents"][i])
                    pergunta_ids.append(results["ids"][i])
            
            # Testar similaridade entre cada par de perguntas
            for i in range(len(pergunta_texts)):
                query_results = collection.query(
                    query_texts=[pergunta_texts[i]],
                    n_results=len(pergunta_texts),
                    where={"type": {"$eq": "pergunta"}}
                )
                
                print(f"\nSimilaridade para pergunta {i+1} (ID: {pergunta_ids[i]}):")
                for j, (id_, distance) in enumerate(zip(query_results["ids"][0], query_results["distances"][0])):
                    if j > 0:  # Pular a própria pergunta
                        print(f"  - Similaridade com {id_}: {distance}")
                        if distance < 0.1:  # Valor muito baixo indica alta similaridade
                            print(f"    ⚠️ ALERTA: Perguntas muito similares detectadas!")
        
    except Exception as e:
        print(f"Erro ao depurar coleção: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        print("Modo de depuração ativado. Mostrando informações da coleção...")
        debug_collection()
    else:
        print("Modo normal. Processando emails não lidos...")
        main()
        
    print("\nPara depurar a coleção, execute: python app.py debug")
