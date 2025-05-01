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
    {"id":"doc5","text":"The quick brown fox jumps over the lazy dog."},
    {"id":"doc6","text":"Artificial intelligence is transforming the world."},
    {"id":"doc7","text":"Can you believe how cold it is today?"},
    {"id":"doc8","text":"She enjoys hiking in the mountains on weekends."},
    {"id":"doc9","text":"The meeting has been rescheduled to next Monday."},
    {"id":"doc10","text":"Bananas are rich in potassium and fiber."},
    {"id":"doc11","text":"Don't forget to lock the door before leaving."},
    {"id":"doc12","text":"I love reading science fiction novels."},
    {"id":"doc13","text":"Our flight departs at 6:45 AM sharp."},
    {"id":"doc14","text":"Please submit your assignment by Friday."}
]

for doc in documents:
    collection.upsert(ids=doc["id"],documents=[doc["text"]])

# define a query text 
query_text = "on weekends"

results = collection.query(
    query_texts=[query_text],
    n_results=2
)

for idx,document in enumerate(results["documents"][0]):
    doc_id = results["ids"][0][idx]
    distance = results["distances"][0][idx]
    print(f" For the query: {query_text}, \n Found similar documents: {document} (ID: {doc_id}, Distance: {distance})")
