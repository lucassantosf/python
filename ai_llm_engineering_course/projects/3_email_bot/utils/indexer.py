from utils.reader import EmailReader
from chromadb.utils import embedding_functions
import chromadb 

print("Indexing emails...")
reader = EmailReader({"seen": True})
emails = reader.read_emails()

default_ef = embedding_functions.DefaultEmbeddingFunction()
chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")

collection = chromadb_client.get_or_create_collection("email_bot",embedding_function=default_ef)

for email in emails:
    print(f"Indexing email from {email['from']} with subject '{email['subject']}'")
    collection.upsert(
        ids=[str(email["id"])],
        documents=[email["text"]],
        metadatas=[{
            "from": email["from"],
            "subject": email["subject"],
            "text": email["text"],
        }]
    )
print("Emails indexed successfully.")

# # Busca semantica
# res = collection.query(
#     query_texts=["cadastro"],
#     n_results=3
# )
# for i in range(len(res["ids"][0])):
#     print(f"Resultado {i + 1}")
#     print(f"ID: {res['ids'][0][i]}")
#     print(f"Documento: {res['documents'][0][i]}")
#     print(f"Metadados: {res['metadatas'][0][i]}")
#     print(f"Distância: {res['distances'][0][i]}")
#     print("---")
# # FIM Busca semantica

# # Busca geral sem query
# results = collection.get()
# for i in range(len(results["ids"])):
#     print(f"ID: {results['ids'][i]}")
#     # print(f"Texto: {results['documents'][i]}")
#     print(f"Metadata: {results['metadatas'][i]}")
#     print("---")
## FIM Busca geral