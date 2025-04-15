from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import pprint
import re

text_loader = TextLoader("./doc/dream.txt")
documents = text_loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
    length_function=len,
)

# Split documents
splits = text_splitter.split_documents(documents)

for i, split in enumerate(splits):
    print(f"Split {i+1} : \n {split} \n")