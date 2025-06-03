from openai import OpenAI
from utils.reader import EmailReader
from utils.sender import EmailSender
from utils.model import LLMModel
from chromadb.utils import embedding_functions
import chromadb

def main():
    reader = EmailReader(params={"seen": False})
    sender = EmailSender()
    emails = reader.read_emails()

    default_ef = embedding_functions.DefaultEmbeddingFunction()
    chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")

    collection = chromadb_client.get_or_create_collection("email_bot",embedding_function=default_ef)

    for email in emails:
        print(f"Creating reply for email {email['from']} subject: {email['subject']}") 

        # Busca semantica
        res = collection.query(
            query_texts=email['text'],
            n_results=1
        )

        for i in range(len(res["ids"][0])):
            # reply = seeder.generate_incident_reply_from_problem(base_problem=problem)
            # print(reply)

            # sender.reply_email(original_msg=email['raw'], reply_body=reply)
            # print("E-mail respondido com sucesso.")  
            print(f"Resultado {i + 1}")
            print(f"ID: {res['ids'][0][i]}")
            print(f"Documento: {res['documents'][0][i]}")
            print(f"Metadados: {res['metadatas'][0][i]}")
            print(f"Distância: {res['distances'][0][i]}")
            print("---")

if __name__ == "__main__":
    main()