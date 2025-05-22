import streamlit as st 
import chromadb
import os 
import PyPDF2
import uuid
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv

# Suppress tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

load_dotenv()

# Constants 
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

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

class SimplePDFProcessor:
    """Handle PDF processing and chunking"""

    def __init__(self,chunk_size=CHUNK_SIZE,chunk_overlap=CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def read_pdf(self, pdf_file):
        """Read PDF and extract text"""
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        return text 

    def create_chunks(self, text, pdf_file):
        """Split text into chuncs"""
        chunks = []
        start = 0

        while start < len(text):
            # Find end of chunk
            end = start + self.chunk_size

            # If not at the start, include overlap
            if start > 0:
                start = start - self.chunk_overlap 

            # Get chunk 
            chunk = text[start:end]

            # Try to break at sentence end
            if end < len(text):
                last_period = chunk.rfind(".")
                if last_period != -1:
                    chunk = chunk[: last_period +1]
                    end = start + last_period + 1

            chunks.append(
                {
                    "id": str(uuid.uuid4()),
                    "text":chunk,
                    "metadata":{"source":pdf_file.name},
                }
            )

            start = end 

        return chunks

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

    # Division of the page into three columns 
    _, col2, _ = st.columns([1, 2, 1])

    with col2:
        st.title("💬 Chat with your documents")

        # File upload
        pdf_file = st.file_uploader("Upload PDF", type="pdf")

        if pdf_file and pdf_file.name not in st.session_state.processed_files:
            # Process PDF
            processor = SimplePDFProcessor()
            with st.spinner("Processing PDF...."):
                try:
                    # Extract text
                    text = processor.read_pdf(pdf_file)
                    # Create chunks 
                    chunks = processor.create_chunks(text,pdf_file)
                    # Add to database
                    if st.session_state.rag_system.add_documents(chunks):
                        st.session_state.processed_files.add(pdf_file.name)
                        st.success(f"Successfully processed {pdf_file.name}")
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")

        # Query interface
        if st.session_state.processed_files:
            st.subheader("Query Your Documents")
            query = st.text_input("Ask a question")

            if query:
                with st.spinner("Generating response..."):
                    # Get relevant chunks
                    results = st.session_state.rag_system.query_documents(query)
                    if results and results["documents"]:
                        # Generate response
                        response = st.session_state.rag_system.generate_response(
                            query, results["documents"][0]
                        )

                        if response:
                            # Display results
                            st.markdown("### Answer:")
                            st.write(response)

                            with st.expander("view Source Passages"):
                                for idx,doc in enumerate(results["documents"][0],1):
                                    st.markdown(f"**Passage {idx}:**")
                                    st.info(doc)

if __name__ == "__main__":
    main()