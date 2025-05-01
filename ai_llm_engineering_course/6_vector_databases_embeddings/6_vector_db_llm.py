import chromadb 
import os
from dotenv import load_dotenv
from openai import OpenAI
from chromadb.utils import embedding_functions

# Load environment variables from .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_api_key,
    model_name="text-embedding-3-small"
)

# Initialize the Chroma client with persistence
chromadb_client = chromadb.PersistentClient(path="./db/chroma_persistent_storage")
collection_name = "document_qa_collection"
collection = chromadb_client.get_or_create_collection(
    name=collection_name,
    embedding_function=openai_ef
)

## This code has two parts: run it in two steps

# # Part 1: Load documents and create embeddings
# # Function to load documents from a directory
# def load_documents_from_directory(directory_path):
#     print("==== Loading documents from directory ====")
#     documents = []
#     for filename in os.listdir(directory_path):
#         if filename.endswith(".txt"):
#             with open(
#                 os.path.join(directory_path,filename),"r",encoding="utf-8"
#             ) as file:
#                 documents.append({"id":filename,"text":file.read()})

#     return documents

# # Function to split text into chuncks
# def split_text(text, chunck_size=1000, chunck_overlap=20):
#     chuncks = []
#     start = 0
#     while start < len(text):
#         end = start + chunck_size
#         chuncks.append(text[start:end])
#         start = end - chunck_overlap
#     return chuncks

# # Load documents from the directory 
# directory_path = "./data/new_articles"
# documents = load_documents_from_directory(directory_path)

# print(f"Loaded {len(documents)} documents")
# print(documents)

# # Split the documents into chuncks
# chunked_documents = []
# for doc in documents:
#     chunks = split_text(doc["text"])
#     print("==== Splitting docs into chunks ====")
#     for i, chunk in enumerate(chunks):
#         chunked_documents.append({"id": f"{doc['id']}_chunk{i+1}", "text": chunk})

# # Function to generate embeddings using OpenAI API
# def get_openai_embedding(text):
#     response = client.embeddings.create(input=text, model="text-embedding-3-small")
#     embedding = response.data[0].embedding
#     print("==== Generating embeddings... ====")
#     return embedding

# # Generate embeddings for the documents chuncks
# for doc in chunked_documents:
#     print("==== Generating embeddings... ====")
#     doc["embedding"] = get_openai_embedding(doc["text"])

# # Upsert documents with embeddings into Chroma
# for doc in chunked_documents:
#     print("==== Inserting chuncks into db... ====")
#     collection.upsert(
#         ids=[doc["id"]], documents=[doc["text"]], embeddings=[doc["embedding"]]
#     )
# # End Part 1: Load documents and create embeddings

# Part 2: Query documents and generate response
# Function to query documents
def query_documents(question, n_results=2):
    # query_embedding = get_openai_embedding(question)
    results = collection.query(query_texts=question, n_results=n_results)

    # Extract the relevant chunks
    relevant_chunks = [doc for sublist in results["documents"] for doc in sublist]
    print("==== Returning relevant chunks ====")
    return relevant_chunks

# Function to generate a response from OpenAI
def generate_response(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)
    prompt = (
        "You are an assistant for question-answering tasks. Use the following pieces of "
        "retrieved context to answer the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the answer concise."
        "\n\nContext:\n" + context + "\n\nQuestion:\n" + question
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )
    answer = response.choices[0].message
    return answer

question = "give me a brief overview of the articles. Be concise, please."
relevant_chunks = query_documents(question)
answer = generate_response(question, relevant_chunks)

print("==== Answer ====")
print(answer.content)
# End Part 2: Query documents and generate response
