from openai import OpenAI
from reader import EmailReader
from sender import EmailSender
import chromadb 
from chromadb.utils import embedding_functions

class LLMModel:
    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:11434/v1",api_key="ollama")
        self.model_name = "llama3.2:1b"

    def generate_completion(self,messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0
            )
            return response.choices[0].message.content 
        except Exception as e:
            return f"Error generating response: {str(e)}" 

def main():
    reader = EmailReader(params={"seen": True})
    sender = EmailSender()
    emails = reader.read_emails()

    default_ef = embedding_functions.DefaultEmbeddingFunction()
    chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")

    collection = chromadb_client.get_or_create_collection("email_bot",embedding_function=default_ef)

    for email in emails:
        //


        print(f"Creating reply for email {email['from']} subject: {email['subject']}") 

        # Busca semantica
        res = collection.query(
            query_texts="Relatorio de desempenho",
            n_results=1
        )
        for i in range(len(res["ids"][0])):

            # STOPPED HERE - ENVIAR RESPOSTA COM O SENDER

            print(f"Resultado {i + 1}")
            print(f"ID: {res['ids'][0][i]}")
            print(f"Documento: {res['documents'][0][i]}")
            print(f"Metadados: {res['metadatas'][0][i]}")
            print(f"Distância: {res['distances'][0][i]}")
            print("---")

if __name__ == "__main__":
    main()