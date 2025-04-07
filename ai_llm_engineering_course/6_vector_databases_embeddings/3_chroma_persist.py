import chromadb 
from chromadb.utils import embedding_functions

default_ef = embedding_functions.DefaultEmbeddingFunction()
chromadb_client = chromadb.PersistentClient(path="./db/chroma_persist")

collection = chromadb_client.get_or_create_collection("my_story",embedding_function=default_ef)

documents = [
    {"id":"doc1","text":"Hello,world!"},
    {"id":"doc2","text":"How are you today?"},
    {"id":"doc3","text":"Goodbye, see you later!"},
    {"id":"doc4","text":"Microsoft is a technology company that developes softwares"},
]

for doc in documents:
    collection.upsert(ids=doc["id"],documents=[doc["text"]])

# define a query text 
query_text = "how are you?"

results = collection.query(
    query_texts=[query_text],
    n_results=2
)

for idx,document in enumerate(results["documents"][0]):
    doc_id = results["ids"][0][idx]
    distance = results["distances"][0][idx]
    print(f" For the query: {query_text}, \n Found similar documents: {document} (ID: {doc_id}, Distance: {distance})")
