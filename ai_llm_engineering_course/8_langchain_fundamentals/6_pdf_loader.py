from langchain_community.document_loaders import (
    TextLoader,
    CSVLoader,
    PyPDFLoader,
    DirectoryLoader,
)

pdf_loader = PyPDFLoader("./doc/linux-manual.pdf")

docs = pdf_loader.load()

print("PDF loaded successfully!",docs)