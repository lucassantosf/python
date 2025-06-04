from openai import OpenAI
from utils.reader import EmailReader
from utils.sender import EmailSender
from utils.model import LLMModel
from chromadb.utils import embedding_functions
import chromadb

def main():
    reader = EmailReader(params={"seen": True})
    sender = EmailSender()
    emails = reader.read_emails()

    print(f"Found {len(emails)} new emails to process.")

    default_ef = embedding_functions.DefaultEmbeddingFunction()
    chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")

    collection = chromadb_client.get_or_create_collection("email_bot",embedding_function=default_ef)

    # DEBUG: não esta salvando respostas
    respostas_gerais = collection.get(
        where={"type": "resposta"},
        limit=5
    )
    print("Algumas respostas armazenadas no banco:")
    print(respostas_gerais["documents"])

    return True


    for email in emails:
        print(f"Creating reply for email {email['from']} subject: {email['subject']}") 

        # Busca semantica
        res = collection.query(
            query_texts=email['text'],
            n_results=1,
            where={"type": "pergunta"},
        )

        if not res["ids"][0]:
            print("Nenhuma pergunta correspondente encontrada.")
            continue

        pergunta_metadata = res["metadatas"][0][0]
        pergunta_id = pergunta_metadata.get("message_id")

        print(f"\n🧠 Pergunta similar encontrada:")
        print(f"Assunto: {pergunta_metadata.get('subject')}")
        print(f"Texto: {res['documents'][0][0]}")

        # Passo 2: Buscar resposta associada a essa pergunta
        resposta_relacionada = collection.query(
            query_texts=["placeholder"],
            n_results=1,
            where={
                "$and": [
                    {"type": "resposta"},
                    {"in_reply_to": pergunta_id}
                ]
            }
        )

        if resposta_relacionada["documents"]:
            resposta_texto = resposta_relacionada["documents"][0]
            print(f"\n💡 Resposta relacionada encontrada:")
            print(resposta_texto)

            # Aqui você poderia gerar uma nova resposta com base nessa resposta anterior
            # reply = model.generate_reply_based_on(resposta_texto, email["text"])
            # sender.reply_email(original_msg=email['raw'], reply_body=reply)
        else:
            print("\n⚠️ Nenhuma resposta associada foi encontrada.")

        print("===")

if __name__ == "__main__":
    main()