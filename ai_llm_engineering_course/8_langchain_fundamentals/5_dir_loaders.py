from langchain_community.document_loaders import (
    TextLoader,
    CSVLoader,
    PyPDFLoader,
    DirectoryLoader,
)

dir_loader = DirectoryLoader("./data/", glob="**/*.txt")
dir_documents = dir_loader.load()   

print("Directory Text Documents:",dir_documents)
