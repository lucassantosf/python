import matplotlib
matplotlib.use("TkAgg")  # precisa estar antes de importar pyplot para ver as imagens

import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
from matplotlib import pyplot as plt
import warnings 

# Suppress all warnings
warnings.filterwarnings("ignore")

# create a chromadb object 
chroma_client = chromadb.PersistentClient(path="./data/chroma.db")

# instantiate image loader
image_loader = ImageLoader()

# instantiate multimodal embedding function
embedding_function = OpenCLIPEmbeddingFunction()

# create the collection, - vector database
collection = chroma_client.get_or_create_collection(
    "multimodal_collection",
    embedding_function=embedding_function,
    data_loader=image_loader,
)

# add images to the collection add() or update() method
# collection.update(
#     ids=["0", "1"],
#     uris=["./images/lion.jpg","./images/tiger.jpg"],
#     metadatas=[{"category": "animal"}, {"category": "animal"}],
# )

# check the count of the collection
# print(f"Collection count: {collection.count()}")

# Simple function to print the results of a query.
# The 'results' is a dict {ids, distances, data , ....}
# Each item in the dict is a 2d list.
def print_query_results(query_list: list, query_results: dict)->None:
    result_count = len(query_results["ids"][0])

    for i, query in enumerate(query_list):
        print(f"Results for query : {query_list[i]}")
        for j in range(result_count):
            id = query_results["ids"][i][j]
            distance = query_results["distances"][i][j] 
            data = query_results["data"][i][j] 
            document = query_results["documents"][i][j] 
            metadata = query_results["metadatas"][i][j] 
            uri = query_results["uris"][i][j] 

            print(f"ID: {id}, Distance: {distance}, Data: {data}, Document: {document}, Metadata: {metadata}, URI: {uri}")

            # Display image, the physical file must exist at URI 
            # (ImageLoader loads the image from file)
            print(f"data: {uri}")
            plt.imshow(data)
            plt.axis("off")
            plt.show()

# It is possible to submit multiple queries at the same time
query_texts = ["tiger"]

# Query vector db - return 3 results
query_results = collection.query(
    query_texts=query_texts,
    n_results=2,
    include=["documents", "metadatas", "distances", "uris", "data"],
)

print_query_results(query_texts, query_results)