from chromadb.utils import embedding_functions 

default_ef = embedding_functions.DefaultEmbeddingFunction()

name = "Lucas"

emb = default_ef(name)

print(emb)