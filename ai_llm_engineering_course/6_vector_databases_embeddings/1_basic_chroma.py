import chromadb
from chromadb.utils import embedding_functions 

default_ef = embedding_functions.DefaultEmbeddingFunction()
chromadb_client = chromadb.Client()

# Create collection
colection_name = "test_collection"
collection = chromadb_client.get_or_create_collection(colection_name, embedding_function=default_ef)

# Define text documents
documents = [
    {"id":"doc1","text":"Hello,world!"},
    {"id":"doc2","text":"How are you today?"},
    {"id":"doc3","text":"Goodbye, see you later!"},
]

for doc in documents:
    collection.upsert(ids=doc["id"],documents=[doc["text"]])

# Define a query text
query_text = "see you"

results = collection.query(
    query_texts=[query_text],
    n_results=3,
)

for idx,document in enumerate(results["documents"][0]):
    doc_id = results["ids"][0][idx]
    distance = results["distances"][0][idx]
    print(f" For the query: {query_text}, \n Found similar documents: {document} (ID: {doc_id}, Distance: {distance})")