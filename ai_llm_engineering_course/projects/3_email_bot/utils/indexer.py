from utils.reader import EmailReader
from chromadb.utils import embedding_functions
import chromadb 

def main():

    print("Indexing emails...")
    reader = EmailReader({"seen": True})
    emails = reader.read_emails()

    default_ef = embedding_functions.DefaultEmbeddingFunction()
    chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")

    collection = chromadb_client.get_or_create_collection("email_bot",embedding_function=default_ef)

    for email in emails:

        # print(f"Indexing email from {email['from']} with subject '{email['subject']}'")
        # print(email)
        
        if email["is_reply"]:

            # Indexa a resposta
            collection.upsert(
                ids=[f"{email['id']}-resposta"],
                documents=[email["text"]],
                metadatas=[{
                    "from": email["from"],
                    "subject": email["subject"],
                    "text": email["text"],
                    "type": "resposta",
                    "in_reply_to": email["in_reply_to"] or "",
                    "message_id": email["message_id"] or ""
                }]
            )

            # Indexa a pergunta original (se extraída)
            if email["original_text"]:
                collection.upsert(
                    ids=[f"{email['id']}-pergunta"],
                    documents=[email["original_text"]],
                    metadatas=[{
                        "from": email["from"],
                        "subject": f"[ENC: {email['subject']}]",
                        "text": email["original_text"],
                        "type": "pergunta",
                        "in_reply_to": "",
                        "message_id": ""  # você não vai saber qual era o ID original nesse caso
                    }]
                )

        else:
            # Email normal (pergunta única)
            collection.upsert(
                ids=[str(email["id"])],
                documents=[email["text"]],
                metadatas=[{
                    "from": email["from"],
                    "subject": email["subject"],
                    "text": email["text"],
                    "type": "pergunta",
                    "in_reply_to": email["in_reply_to"] or "",
                    "message_id": email["message_id"] or ""
                }]
            )

    print("Emails indexed successfully.")

if __name__ == "__main__":
    main()