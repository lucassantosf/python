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

        tipo = "resposta" if email["is_reply"] else "pergunta"
        
        print(f"Indexing email from {email['from']} with subject '{email['subject']}'")
        
        # DEBUG: não esta salvando o tipo correto, ta tudo vazio
        print({
            "from": email["from"],
            "subject": email["subject"],
            "text": email["text"],
            "type": tipo,
            "in_reply_to": email["in_reply_to"] or "",
            "message_id": email["message_id"] or ""
        })

        # collection.upsert(
        #     ids=[str(email["id"])],
        #     documents=[email["text"]],
        #     metadatas=[{
        #         "from": email["from"],
        #         "subject": email["subject"],
        #         "text": email["text"],
        #         "type": tipo,
        #         "in_reply_to": email["in_reply_to"] or "",
        #         "message_id": email["message_id"] or ""
        #     }]
        # )

    print("Emails indexed successfully.")

if __name__ == "__main__":
    main()