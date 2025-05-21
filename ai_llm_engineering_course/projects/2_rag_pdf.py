# import libraries for frontend
import streamlit as st

# import libraries for backend
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

class SimpleRAGSystem:
    """Simple RAG implementation"""

    def __init__(self, embedding_model="chroma",llm_model="ollama"):
        self.embedding_model = embedding_model
        self.llm_model = llm_model

        # Initialize ChromaDB
        self.db = chromadb.PersistentClient(path="./chroma_db")

        # Setup embedding function based on model
        self.setup_embedding_function()

        # Setup LLM
        self.llm = OpenAI(base_url="http://localhost:11434/v1",api_key="ollama")

        # Get or create collection with proper handling
        self.collection = self.setup_collection()

    def setup_embedding_function(self):
        """Setup the appropriate embedding function"""
        try:
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        except Exception as e:
            st.error(f"Error setting up embedding function: {str(e)}")
            raise e

    def setup_collection(self):
        """Setup collection with proper dimension handling"""
        collection_name = f"documents_{self.embedding_model}"
        try:
            # Try to get existing collection firts
            try:
                collection = self.db.get_collection(
                    name=collection_name, embedding_function=self.embedding_fn
                )
                st.info(
                    f"Using existing collection for {self.embedding_model} embedding model"
                )

            except:
                # If collection doesn't exist, create new one
                collection = self.db.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_fn,
                    metadata={"model":self.embedding_model}
                )
                
            return collection

        except Exception as e:
            st.error(f"Error setting up collection: {str(e)}")
            raise e 
    
    def add_documents(self,chunks):
        """Add documents to ChromaDB"""
        try:
            # Ensure collection exists
            if not self.collection:
                self.collection = self.setup_collection()

            # Add documents
            self.collection.add(
                ids=[chunk["id"] for chunk in chunks],
                documents = [chunk["text"] for chunk in chunks],
                metadatas = [chunk["metadata"] for chunk in chunks],
            )
            return True
        except Exception as e:
            st.error(f"Error setting up collection: {str(e)}")
            return False

    def query_documents(self, query, n_results=3):
        """Query documents and return relevants chuncks"""
        try: 
            # Ensure collection exists 
            if not self.collection:
                raise ValueError("No collection available")

            results = self.collection.query(query_texts=[query],n_results=n_results)
            return results

        except Exception as e:
            st.error(f"Error quering documents: {str(e)}")
            return False

    def generate_response(self,query,context):
        """Generate response using LLM"""
        try:
            prompt = f"""
                Based on the following context, please answer the question,
                If you can't find the answer in the context, say so, or I dont know.

                Context: {context}

                Question: {query}

                Answer:
            """

            response = self.llm.chat.completions.create(
                model="llama3.2:1b",
                messages=[
                    {"role":"system","content":"You are a helpful assistant"},
                    {"role":"user","content":prompt}
                ]
            )

            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return None

    def get_embedding_info(self):
        """Get information about current embedding model"""
        model_selector = SimpleModelSelector()
        model_info = model_selector.embedding_models[self.embedding_model]
        return {
            "name": model_info["name"],
            "dimensions": model_info["dimensions"],
            "model": self.embedding_model,
        } 

def main():
    
    st.set_page_config(page_title="PDF Summarizer", layout="wide")

    # Initialize session state
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()
    if "current_embedding_model" not in st.session_state:
        st.session_state.current_embedding_model = set()
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = None
 
    # Initialize RAG System
    try:
        if st.session_state.rag_system is None:
            st.session_state.rag_system = SimpleRAGSystem()
 
    except Exception as e:
        st.error(f"Error initializing RAG system: {str(e)}")
        return 

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:

        st.title("💬 Chat with your documents")

        # File upload
        pdf_file = st.file_uploader("Upload PDF", type="pdf")

        st.write("Ask your question about your PDF here:")

        if "history" not in st.session_state:
            st.session_state.history = []

        # Caixa de texto que envia ao pressionar Enter
        user_input = st.text_input('') 

if __name__ == "__main__":
    main()