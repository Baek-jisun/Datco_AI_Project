import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from chromadb.config import Settings
from config import DB_PATH, UPLOAD_DIR
from utils import clean_text

class RAGEngine:
    def __init__(self):
        self.compression_retriever = None
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    def setup_engine(self):
        if not os.path.exists(UPLOAD_DIR) or not os.listdir(UPLOAD_DIR):
            return None
        
        all_docs = []
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(os.path.join(UPLOAD_DIR, filename))
                docs = loader.load()
                for doc in docs:
                    doc.page_content = clean_text(doc.page_content)
                
                splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=150)
                all_docs.extend(splitter.split_documents(docs))
        
        if not all_docs:
            return None
        
        vectorstore = Chroma(
            persist_directory=DB_PATH, 
            embedding_function=self.embeddings, 
            client_settings=Settings(is_persistent=True, anonymized_telemetry=False)
        )
        
        bm25 = BM25Retriever.from_documents(all_docs)
        vector_r = vectorstore.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 6} 
        )

        self.compression_retriever = EnsembleRetriever(
            retrievers=[bm25, vector_r], 
            weights=[0.3, 0.7]
        )
        return self.compression_retriever

rag_engine = RAGEngine()