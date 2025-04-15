from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import pprint
import re

load_dotenv()

documents = TextLoader("./doc/dream.txt").load()

# Data cleaning function
def clean_text(text):
    # Remove unwanted characters (e.g, digits, special characters)
    text = re.sub(r"[^a-zA-Z\s]", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Convert to lowercase
    text = text.lower()

    return text

# Clean the text
cleaned_documents = [clean_text(doc.page_content) for doc in documents]

# Split the text into characters 
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = text_splitter.split_documents(documents)

#Cleanup the text
texts = [clean_text(text.page_content) for text in texts]

# Load the OpenAI embeddings to vectorize the text 
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create the retriever from the loaded embeddings and documents
retriever = FAISS.from_texts(texts,embeddings).as_retriever(
    search_kwargs={"k": 3}
)

# Query the retriever
query = "What did Martin Luther King Jr. dream about?"
docs = retriever.invoke(query, k=1)

pprint.pprint(f" => Docs: {docs}:")

# chat with the model and our docs

