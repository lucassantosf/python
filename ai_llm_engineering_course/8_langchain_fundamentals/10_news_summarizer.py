import os 
from typing import Optional
from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama

from langchain.schema import Document 
from newspaper import Article 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv

load_dotenv()

class NewsArticleSummarizer:
    def __init__(
        self,
        api_key: str = None,
        model_type: str = "openai",
        model_name: str = "gpt-4o-mini",
    ):
        """
            Initialize the summarizer with choice of model:
            Args:
                api_key (str): API key for OpenAI or Ollama.
                model_type (str): Type of model to use ('openai' or 'ollama').
                model_name (str): Name of the model to use.
        """
        self.model_type = model_type
        self.model_name = model_name

        # Setup LLM based on model type
        if model_type == "openai":
            if not api_key:
                raise ValueError("API key is required for OpenAI model.")
            os.environ["OPENAI_API_KEY"] = api_key
            self.llm = ChatOpenAI(model_name=model_name, temperature=0)
        elif model_type == "ollama":
            self.llm = ChatOllama(
                model=model_name,
                temperature=0,
                format="json", 
                timeout=120, 
            )
        else:
            raise ValueError(f"Unsupported model type. {model_type}") 

        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200, length_function=len)

    def fetch_article(self, url: str) -> Optional[Article]:
        """
            Fetch article content using newspaper3k
        """
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article
        except Exception as e:
            print(f"Error fetching article: {str(e)}")
            return None

    def create_documents(self, text: str) -> list[Document]:
        """
            Create Langchain documents from text
        """
        texts = self.text_splitter.split_text(text)
        docs = [Document(page_content=t) for t in texts]
        return docs

    def summarize(self,url:str, summary_type: str="detailed")-> dict:
        """
            Main summarization pipeline
        """
        article = self.fetch_article(url)
        if not article:
            return {"error": "Failed to fetch article content."}

        docs = self.create_documents(article.text)

        # Create documents
        docs = self.create_documents(article.text)


        # Define prompts based on summary type
        if summary_type == "detailed":
            map_prompt_template = """Write a detailed summary of the following text:
            "{text}"
            DETAILED SUMMARY:"""
            combine_prompt_template = """Write a detailed summary of the following text that combines the previus summaries:
            "{text}"
            FINAL DETAILED SUMMARY:"""
        else: 
            map_prompt_template = """Write a concise summary of the following text:
            "{text}"
            CONCISE SUMMARY:"""
            combine_prompt_template = """Write a concise summary of the following text that combines the previus summaries::
            "{text}"
            FINAL CONCISE SUMMARY:"""

        # Create prompts
        map_prompt = PromptTemplate(
            input_variables=["text"],
            template=map_prompt_template,
        )
        combine_prompt = PromptTemplate(
            input_variables=["text"],
            template=combine_prompt_template,
        )

        # Create the run chain
        chain = load_summarize_chain(
            llm=self.llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            verbose=True,
        )

        # Generate summary
        summary = chain.invoke(docs)

        return {
            "title": article.title,
            "authors": article.authors,
            "publish_date": article.publish_date,
            "summary": summary,
            "url": url,
            "model_info": {
                "type": self.model_type,
                "name": self.model_name,
            },
        }

def main():
    # Example of using both models
    url = "https://beebom.com/what-is-nft-explained/" 

    # Initialize both summarizers
    openai_summarizer = NewsArticleSummarizer(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_type="openai",
        model_name="gpt-4o-mini",
    )
    ollama_summarizer = NewsArticleSummarizer(
        model_type="ollama",
        model_name="llama3.2:1b",
    )

    # Get summaries from both models 
    print("\n Generating OpenAi Summary ... ")
    openai_summary = openai_summarizer.summarize(url, summary_type="detailed")
    print("\n Generating Llama Summary ... ")
    llama_summary = ollama_summarizer.summarize(url, summary_type="detailed")

    # Print summaries 
    for model, summary in [(openai_summary,"OpenAI"), (llama_summary,"Llama")]:
        print(f"\n{model} Summary:")
        print(f"Title: {summary['title']}")
        print(f"Authors: {summary['authors']}")
        print(f"Publish Date: {summary['publish_date']}")
        print(f"Summary: {summary['summary']}")
        print(f"URL: {summary['url']}")
        print(f"Model Info: {summary['model_info']}")

        # Print first document content
        print(f"\nFirst Document Content: {summary['docs'][0].page_content}")
        print(f"\nSecond Document Content: {summary['docs'][2].page_content}")

if __name__ == "__main__":
    main()