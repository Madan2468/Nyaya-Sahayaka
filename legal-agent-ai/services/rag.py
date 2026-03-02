import os
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class RAGService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        # Recommend using a public multilingual model from HF for Indian Languages
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self.vector_store_path = os.path.join(data_dir, "faiss_index")
        
        # Load index if exists, otherwise it needs to be built by ingest.py
        if os.path.exists(self.vector_store_path):
            self.vector_store = FAISS.load_local(
                self.vector_store_path, 
                self.embeddings,
                allow_dangerous_deserialization=True # required for trusted local FAISS files
            )
        else:
            self.vector_store = None
            print("FAISS index not found. Please run ingest.py first.")

    def retrieve(self, query: str, top_k: int = 5, intent: str = None):
        if not self.vector_store:
            return "No legal database found. Searching for general advice."
        
        # FAISS kwargs support
        kwargs = {"k": top_k}
        if intent:
            kwargs["filter"] = {"type": intent}

        try:
            docs = self.vector_store.similarity_search(query, **kwargs)
        except Exception:
            # Fallback if FAISS filter encounters issues
            docs = self.vector_store.similarity_search(query, k=top_k)
        
        # Format retrived documents
        context = ""
        for d in docs:
            # Assuming metadata has Source like IPC, CrPC, Scheme Name
            source = d.metadata.get("source", "Unknown Legal Source")
            section = d.metadata.get("section", "N/A")
            context += f"\n[{source} - {section}]: {d.page_content}\n"
            
        return context
