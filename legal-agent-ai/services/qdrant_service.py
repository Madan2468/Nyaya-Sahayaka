import os
import threading
from typing import Optional, List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class QdrantRAGService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(QdrantRAGService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, host: str = None, port: int = 6333, data_dir: str = None):
        if getattr(self, '_initialized', False):
            return

        if data_dir is None:
            # Default to data folder inside legal-agent-ai
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
        self.data_dir = data_dir
        self.url = os.environ.get("QDRANT_URL")
        self.api_key = os.environ.get("QDRANT_API_KEY")
        self.host = host or os.environ.get("QDRANT_HOST", "localhost")
        self.port = int(os.environ.get("QDRANT_PORT", port))
        self.collection_name = "nyaya_legal_and_schemes"
        self.vector_size = 384  # paraphrase-multilingual-MiniLM-L12-v2 dimensionality
        
        # Load embedding model once
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # Connect to Qdrant (try Qdrant Cloud first, then local Docker, then embedded)
        self.client = None
        self.is_connected = False
        self._init_client()
        self._initialized = True

    def _init_client(self):
        # 1. Try Qdrant Cloud if URL is provided
        if self.url:
            try:
                client = QdrantClient(url=self.url, api_key=self.api_key, timeout=10)
                client.get_collections()
                self.client = client
                self.is_connected = True
                self._ensure_collection()
                print(f"[QdrantRAGService] Connected to Qdrant Cloud at {self.url[:35]}...")
                return
            except Exception as e:
                print(f"[QdrantRAGService] Qdrant Cloud connection failed ({e}). Checking local/embedded...")

        # 2. Try local Docker Qdrant
        try:
            client = QdrantClient(host=self.host, port=self.port, timeout=5)
            client.get_collections()
            self.client = client
            self.is_connected = True
            self._ensure_collection()
            print(f"[QdrantRAGService] Connected to local Qdrant at {self.host}:{self.port}")
            return
        except Exception as e:
            print(f"[QdrantRAGService] Local Qdrant unavailable ({e}). Checking local embedded storage...")

        # 3. Fallback to embedded disk storage
        storage_path = os.path.join(self.data_dir, "qdrant_storage")
        try:
            self.client = QdrantClient(path=storage_path)
            self.is_connected = True
            self._ensure_collection()
            print(f"[QdrantRAGService] Operating with embedded Qdrant storage at '{storage_path}'")
        except Exception as e:
            print(f"[QdrantRAGService] Warning: Could not initialize embedded Qdrant ({e}).")
            self.client = None
            self.is_connected = False

    def _ensure_collection(self):
        """Creates collection and payload indices if they don't already exist."""
        if not self.client:
            return
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=self.vector_size,
                        distance=qmodels.Distance.COSINE
                    )
                )
                print(f"[QdrantRAGService] Created collection '{self.collection_name}'.")

            # Create payload indices for fast filtered search
            for field in ["metadata.type", "metadata.state", "metadata.source", "metadata.section"]:
                try:
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field,
                        field_schema=qmodels.PayloadSchemaType.KEYWORD
                    )
                except Exception:
                    pass
        except Exception as e:
            print(f"[QdrantRAGService] Collection verification notice: {e}")

    def retrieve(
        self,
        query: str,
        top_k: int = 6,
        intent: Optional[str] = None,
        state: Optional[str] = None,
        category: Optional[str] = None
    ) -> str:
        """
        Performs hybrid retrieval:
        1. Comprehensive Indian Statutory DB search (IPC, CrPC, BNS, BNSS, IT Act)
        2. Vector similarity search in Qdrant with metadata filtering and payload matching
        """
        from services.legal_db import search_legal_statutes, format_statutes_for_llm

        legal_context = ""
        is_legal_query = intent == "legal" or any(
            w in query.lower() for w in [
                "ipc", "crpc", "bns", "bnss", "section", "fir", "police", "bail", "arrest",
                "court", "cheating", "fraud", "theft", "murder", "assault", "threat", "dowry",
                "chori", "dhokha", "marpeet", "dhamki", "dahej", "zamanat", "law", "offence"
            ]
        )

        if is_legal_query:
            matched_statutes = search_legal_statutes(query, top_k=4)
            if matched_statutes:
                legal_context = format_statutes_for_llm(matched_statutes)

        if not self.is_connected or not self.client:
            if legal_context:
                return legal_context
            return "No vector database connection found. Running on baseline knowledge."

        try:
            import re
            exact_section_hit = ""

            # Check if query asks for a specific section number (e.g., "302", "Section 302", "IPC 302", "CrPC 154")
            sec_match = re.search(r'\b(?:section|sec|ipc|crpc|bns|bnss)?\s*(\d+[a-z]?)\b', query, re.I)
            if sec_match and (intent == "legal" or is_legal_query):
                raw_sec = sec_match.group(1)
                sec_variants = [raw_sec, f"IPC_{raw_sec}", f"CRPC_{raw_sec}", f"Section {raw_sec}"]
                for sec_var in sec_variants:
                    sec_filter = qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(
                                key="metadata.type",
                                match=qmodels.MatchValue(value="legal")
                            ),
                            qmodels.FieldCondition(
                                key="metadata.section",
                                match=qmodels.MatchValue(value=sec_var)
                            )
                        ]
                    )
                    res = self.client.query_points(
                        collection_name=self.collection_name,
                        query_filter=sec_filter,
                        limit=2
                    ) if hasattr(self.client, "query_points") else None

                    hits = res.points if res else []
                    if hits:
                        for hit in hits:
                            payload = hit.payload or {}
                            content = payload.get("page_content", "")
                            meta = payload.get("metadata", {})
                            sec_val = meta.get("section", sec_var)
                            exact_section_hit += f"\n[IPC/CrPC - Section {sec_val}]: {content}\n"
                        break

            query_vector = self.embeddings.embed_query(query)
            
            # Construct Qdrant filter conditions
            must_conditions = []
            if intent:
                must_conditions.append(
                    qmodels.FieldCondition(
                        key="metadata.type",
                        match=qmodels.MatchValue(value=intent)
                    )
                )
            
            # If state specified and searching for schemes, match state
            if state and intent == "scheme" and state.lower() not in ("all", "all india", ""):
                must_conditions.append(
                    qmodels.FieldCondition(
                        key="metadata.state",
                        match=qmodels.MatchValue(value=state)
                    )
                )

            q_filter = qmodels.Filter(must=must_conditions) if must_conditions else None

            # Use modern query_points API or fallback to legacy search
            if hasattr(self.client, "query_points"):
                res = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    query_filter=q_filter,
                    limit=top_k
                )
                search_results = res.points
                if not search_results and q_filter:
                    res = self.client.query_points(
                        collection_name=self.collection_name,
                        query=query_vector,
                        limit=top_k
                    )
                    search_results = res.points
            else:
                search_results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    query_filter=q_filter,
                    limit=top_k
                )
                if not search_results and q_filter:
                    search_results = self.client.search(
                        collection_name=self.collection_name,
                        query_vector=query_vector,
                        limit=top_k
                    )

            vector_context = exact_section_hit
            for hit in search_results:
                payload = hit.payload or {}
                content = payload.get("page_content", "")
                meta = payload.get("metadata", {})
                source = meta.get("source", "Legal Source")
                sec = meta.get("section", "")
                header = f"[{source} - Section {sec}]" if sec else f"[{source}]"
                if header not in vector_context and header not in legal_context:
                    vector_context += f"\n{header}: {content}\n"

            combined = ""
            if legal_context:
                combined += f"Statutory Database Provisions:\n{legal_context}\n"
            if vector_context.strip():
                combined += f"\nVector Database Records:\n{vector_context}\n"

            return combined.strip() if combined.strip() else (legal_context or "No direct statutory matches in vector database.")
        except Exception as e:
            print(f"[QdrantRAGService] Search failed ({e}), using statutory database.")
            return legal_context or "Vector search unavailable."


def get_qdrant_service() -> QdrantRAGService:
    """Returns the singleton instance of QdrantRAGService."""
    return QdrantRAGService()
