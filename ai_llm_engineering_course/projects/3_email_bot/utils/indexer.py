from utils.reader import EmailReader
from chromadb.utils import embedding_functions
import chromadb 

def main():

    print("Indexing emails...")

    reader = EmailReader()
    emails = reader.read_emails(max_results=5, query='is:unread')

    print("Total emails read:", len(emails))

    default_ef = embedding_functions.DefaultEmbeddingFunction()
    chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")

    collection = chromadb_client.get_or_create_collection("email_bot",embedding_function=default_ef)

    for email in emails:
        email_id = email.get("id") or email.get("message_id")
        if not email_id:
            print("Email sem id encontrado, pulando...")
            continue

        is_reply = email.get("is_reply", False) or bool(email.get("in_reply_to"))

        if is_reply:
            collection.upsert(
                ids=[f"{email_id}-resposta"],
                documents=[email["text"]],
                metadatas=[{
                    "from": email["from"],
                    "subject": email["subject"],
                    "text": email["text"],
                    "type": "resposta",
                    "in_reply_to": email.get("in_reply_to", ""),
                    "message_id": email.get("message_id", "")
                }]
            )

            if email.get("original_text"):
                collection.upsert(
                    ids=[f"{email_id}-pergunta"],
                    documents=[email["original_text"]],
                    metadatas=[{
                        "from": email["from"],
                        "subject": f"[ENC: {email['subject']}]",
                        "text": email["original_text"],
                        "type": "pergunta",
                        "in_reply_to": "",
                        "message_id": ""
                    }]
                )

        else:
            collection.upsert(
                ids=[str(email_id)],
                documents=[email["text"]],
                metadatas=[{
                    "from": email["from"],
                    "subject": email["subject"],
                    "text": email["text"],
                    "type": "pergunta",
                    "in_reply_to": email.get("in_reply_to", ""),
                    "message_id": email.get("message_id", "")
                }]
            )

def show_indexed_emails():
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")

    collection = chromadb_client.get_collection("email_bot")

    # Buscar todos os documentos e metadados
    results = collection.get(include=["documents", "metadatas"])

    for i, (id_, doc, meta) in enumerate(zip(results["ids"], results["documents"], results["metadatas"]), start=1):
        print(f"{i}) ID: {id_}")
        print(f"   Document: {doc}")
        print(f"   Metadata: {meta}")
        print("-" * 40)

if __name__ == "__main__":
    show_indexed_emails()
    # main()