from utils.reader import EmailReader
from chromadb.utils import embedding_functions
import chromadb 
import os
import re

def main():
    """
    Função principal para indexar emails e suas respostas.
    Esta função limpa a coleção existente e reindexar tudo do zero.
    """
    print("Indexando todos os emails...")
    
    # Configurar ChromaDB
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    # Garantir que o diretório existe
    os.makedirs("./db/chroma_persist", exist_ok=True)
    
    try:
        chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
        
        # Verificar se a coleção existe e deletá-la
        try:
            collection = chromadb_client.get_collection("email_bot")
            print("Coleção existente encontrada. Deletando...")
            chromadb_client.delete_collection("email_bot")
            print("Coleção deletada com sucesso.")
        except Exception as e:
            print(f"Nenhuma coleção existente encontrada ou erro ao deletar: {e}")
        
        # Criar uma nova coleção
        collection = chromadb_client.create_collection("email_bot", embedding_function=default_ef)
        print("Nova coleção criada com sucesso.")
        
        # Ler emails
        reader = EmailReader()
        emails = reader.read_emails(max_results=10, query='')
        print(f"Total de emails lidos: {len(emails)}")
        
        # Agrupar emails por thread_id
        threads = {}
        for email in emails:
            thread_id = email['thread_id']
            if thread_id not in threads:
                threads[thread_id] = []
            threads[thread_id].append(email)
        
        print(f"Total de threads: {len(threads)}")
        
        # Processar cada thread
        for thread_id, thread_emails in threads.items():
            print(f"\nProcessando thread {thread_id} com {len(thread_emails)} emails")
            
            if len(thread_emails) == 0:
                continue
                
            # O primeiro email é a pergunta
            original_email = thread_emails[0]
            question_id = f"{thread_id}-pergunta"
            
            # Preparar metadados da pergunta, garantindo que não haja valores None
            question_metadata = {
                "from": original_email.get("from", ""),
                "subject": original_email.get("subject", ""),
                "text": original_email.get("text", ""),
                "type": "pergunta",
                "thread_id": thread_id,
                "message_id": original_email.get("message_id", ""),
                "has_response": len(thread_emails) > 1
            }
            
            # Garantir que nenhum valor seja None
            for key, value in list(question_metadata.items()):
                if value is None:
                    question_metadata[key] = ""
            
            # Armazenar a pergunta
            collection.add(
                ids=[question_id],
                documents=[original_email["text"]],
                metadatas=[question_metadata]
            )
            
            print(f"Pergunta indexada com ID: {question_id}")
            
            # Se houver mais emails, o último é a resposta
            if len(thread_emails) > 1:
                response_email = thread_emails[-1]
                response_id = f"{thread_id}-resposta"
                
                # Preparar metadados, garantindo que não haja valores None
                response_metadata = {
                    "from": response_email.get("from", ""),
                    "subject": response_email.get("subject", ""),
                    "text": response_email.get("text", ""),
                    "type": "resposta",
                    "thread_id": thread_id,
                    "message_id": response_email.get("message_id", ""),
                    "in_reply_to": original_email.get("message_id", ""),
                    "original_question": original_email.get("text", ""),
                    "original_subject": original_email.get("subject", "")
                }
                
                # Garantir que nenhum valor seja None
                for key, value in list(response_metadata.items()):
                    if value is None:
                        response_metadata[key] = ""
                
                # Armazenar a resposta
                collection.add(
                    ids=[response_id],
                    documents=[response_email["text"]],
                    metadatas=[response_metadata]
                )
                
                print(f"Resposta indexada com ID: {response_id}")
                
                # Preparar metadados atualizados da pergunta, garantindo que não haja valores None
                updated_question_metadata = {
                    "from": original_email.get("from", ""),
                    "subject": original_email.get("subject", ""),
                    "text": original_email.get("text", ""),
                    "type": "pergunta",
                    "thread_id": thread_id,
                    "message_id": original_email.get("message_id", ""),
                    "has_response": True,
                    "response_id": response_id
                }
                
                # Garantir que nenhum valor seja None
                for key, value in list(updated_question_metadata.items()):
                    if value is None:
                        updated_question_metadata[key] = ""
                
                # Atualizar a pergunta para indicar que tem resposta
                collection.update(
                    ids=[question_id],
                    metadatas=[updated_question_metadata]
                )
                
                print(f"Pergunta atualizada com referência à resposta: {response_id}")
        
        print("\nIndexação concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro durante a indexação: {e}")

def debug_question_answer_pairs():
    """
    Função específica para depurar os pares de pergunta-resposta no banco de dados.
    Mostra detalhadamente cada pergunta e sua resposta correspondente.
    """
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    try:
        chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
        collection = chromadb_client.get_collection("email_bot")
    except Exception as e:
        print(f"Erro ao acessar a coleção: {e}")
        print("Verifique se a coleção foi criada executando a função main() primeiro.")
        return

    # Buscar todos os documentos e metadados
    results = collection.get(include=["documents", "metadatas"])

    # Separar perguntas e respostas
    perguntas = []
    respostas = []
    
    for i, meta in enumerate(results["metadatas"]):
        if meta.get("type") == "pergunta":
            perguntas.append((i, results["ids"][i], results["documents"][i], meta))
        elif meta.get("type") == "resposta":
            respostas.append((i, results["ids"][i], results["documents"][i], meta))
    
    print(f"\n=== RESUMO DA DEPURAÇÃO ===")
    print(f"Total de documentos: {len(results['ids'])}")
    print(f"Perguntas encontradas: {len(perguntas)}")
    print(f"Respostas encontradas: {len(respostas)}")
    print("=" * 50)
    
    # Verificar se há respostas
    if len(respostas) == 0:
        print("\n⚠️ ALERTA: Nenhuma resposta encontrada no banco de dados!")
        print("Verifique se o processo de indexação está identificando corretamente as respostas.")
        print("Possíveis causas:")
        print("1. Os emails de resposta não estão sendo reconhecidos como respostas")
        print("2. A condição 'is_reply or has_citation' não está sendo satisfeita")
        print("3. Não há emails de resposta nas threads")
        print("\nVerifique os emails originais e certifique-se de que há respostas.")
    else:
        print(f"\n✅ {len(respostas)} respostas encontradas no banco de dados.")
    
    # Mostrar todas as respostas detalhadamente
    print("\n=== TODAS AS RESPOSTAS ENCONTRADAS ===")
    for i, id_, doc, meta in respostas:
        print(f"\nResposta ID: {id_}")
        print(f"Thread ID: {meta.get('thread_id')}")
        print(f"De: {meta.get('from')}")
        print(f"Assunto: {meta.get('subject')}")
        print(f"Em resposta a: {meta.get('in_reply_to')}")
        print(f"Texto completo da resposta:\n{doc}")
        print("-" * 50)
    
    # Mostrar todos os pares pergunta-resposta
    print("\n=== PARES PERGUNTA-RESPOSTA DETALHADOS ===")
    for i, id_, doc, meta in perguntas:
        print(f"\nPergunta ID: {id_}")
        print(f"Thread ID: {meta.get('thread_id')}")
        print(f"De: {meta.get('from')}")
        print(f"Assunto: {meta.get('subject')}")
        print(f"Tem resposta: {meta.get('has_response', False)}")
        print(f"Texto completo da pergunta:\n{doc}")
        
        # Se tiver resposta, mostrar
        if meta.get("has_response") and meta.get("response_id"):
            response_id = meta.get("response_id")
            print(f"Response ID referenciado: {response_id}")
            
            # Listar todos os IDs de resposta disponíveis para depuração
            available_response_ids = [r_id for _, r_id, _, _ in respostas]
            print(f"IDs de resposta disponíveis: {available_response_ids}")
            
            # Verificar se o ID da resposta está na lista de IDs disponíveis
            if response_id in available_response_ids:
                print(f"✅ ID de resposta encontrado na lista de respostas disponíveis")
            else:
                print(f"❌ ID de resposta NÃO encontrado na lista de respostas disponíveis")
            
            # Buscar a resposta correspondente
            found_response = False
            for j, r_id, r_doc, r_meta in respostas:
                print(f"Comparando '{r_id}' com '{response_id}'")
                if r_id == response_id:
                    found_response = True
                    print(f"\nResposta correspondente:")
                    print(f"De: {r_meta.get('from')}")
                    print(f"Assunto: {r_meta.get('subject')}")
                    print(f"Texto completo da resposta:\n{r_doc}")
                    break
            
            if not found_response:
                print("\n⚠️ Resposta referenciada mas não encontrada!")
                print("Tentando buscar por thread_id em vez de response_id...")
                
                # Tentar encontrar por thread_id
                thread_id = meta.get("thread_id")
                expected_response_id = f"{thread_id}-resposta"
                print(f"Thread ID: {thread_id}, Expected Response ID: {expected_response_id}")
                
                for j, r_id, r_doc, r_meta in respostas:
                    if r_id == expected_response_id or r_meta.get("thread_id") == thread_id:
                        print(f"\nResposta encontrada por thread_id:")
                        print(f"ID: {r_id}")
                        print(f"De: {r_meta.get('from')}")
                        print(f"Assunto: {r_meta.get('subject')}")
                        print(f"Texto completo da resposta:\n{r_doc}")
                        
                        # Corrigir o problema atualizando a coleção
                        print("\n🔄 Corrigindo a referência na coleção...")
                        try:
                            default_ef = embedding_functions.DefaultEmbeddingFunction()
                            chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
                            collection = chromadb_client.get_collection("email_bot")
                            
                            # Atualizar o metadado da pergunta com o ID correto da resposta
                            collection.upsert(
                                ids=[id_],
                                documents=[doc],
                                metadatas=[{
                                    **meta,
                                    "response_id": r_id
                                }]
                            )
                            print("✅ Referência corrigida com sucesso!")
                        except Exception as e:
                            print(f"❌ Erro ao corrigir referência: {e}")
                        
                        break
                else:
                    print("\n❌ Não foi possível encontrar uma resposta para esta pergunta.")
        else:
            print("\n⚠️ Esta pergunta não tem resposta associada.")
        
        print("-" * 50)

def search_questions(query_text, n_results=1):
    """
    Busca perguntas similares ao texto da consulta e retorna as perguntas e respostas correspondentes.
    
    Args:
        query_text (str): O texto da consulta para buscar perguntas similares
        n_results (int): Número de resultados a retornar
        
    Returns:
        list: Lista de dicionários contendo perguntas e respostas
    """
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    try:
        chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")
        collection = chromadb_client.get_collection("email_bot")
    except Exception as e:
        print(f"Erro ao acessar a coleção: {e}")
        print("Verifique se a coleção foi criada executando a função main() primeiro.")
        return []
    
    # Buscar apenas documentos do tipo "pergunta"
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={"type": "pergunta"}
    )
    
    qa_pairs = []
    
    if not results["ids"] or len(results["ids"][0]) == 0:
        print("Nenhum resultado encontrado.")
        return []
    
    print(f"\n=== RESULTADOS DA BUSCA PARA: '{query_text}' ===")
    
    for i, (id_, doc, meta) in enumerate(zip(results["ids"][0], results["documents"][0], results["metadatas"][0])):
        print(f"\n{i+1}) Pergunta: {meta.get('subject')}")
        print(f"   De: {meta.get('from')}")
        print(f"   Similaridade: {results['distances'][0][i]}")
        print(f"   Texto: {doc[:150]}...")
        
        qa_pair = {
            "question_id": id_,
            "question": doc,
            "question_subject": meta.get("subject"),
            "question_from": meta.get("from"),
            "has_response": meta.get("has_response", False),
            "response": None,
            "response_text": None
        }
        
        # Se tiver resposta, buscar e mostrar
        if meta.get("has_response") and meta.get("response_id"):
            response_id = meta.get("response_id")
            response_results = collection.get(ids=[response_id], include=["documents", "metadatas"])
            
            if response_results["ids"]:
                resp_doc = response_results["documents"][0]
                resp_meta = response_results["metadatas"][0]
                
                print(f"\n   RESPOSTA:")
                print(f"   De: {resp_meta.get('from')}")
                print(f"   Assunto: {resp_meta.get('subject')}")
                print(f"   Texto completo da resposta:\n{resp_doc}")
                
                qa_pair["response"] = resp_doc
                qa_pair["response_from"] = resp_meta.get("from")
                qa_pair["response_subject"] = resp_meta.get("subject")
            else:
                print("   (Resposta referenciada mas não encontrada)")
        else:
            print("   (Sem resposta)")
        
        print("-" * 40)
        qa_pairs.append(qa_pair)
    
    return qa_pairs

if __name__ == "__main__":

    # Descomente a função que deseja executar
    # Exemplo de uso: primeiro indexar os emails e depois buscar por uma pergunta

    main()  # Indexar todos os emails
    debug_question_answer_pairs()  # Verificar os pares pergunta-resposta
    search_questions("problema com login", n_results=2)  # Buscar perguntas similares