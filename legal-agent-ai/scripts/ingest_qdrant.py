import os
import uuid
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# Load .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_qdrant_client(host: str = "localhost", port: int = 6333, data_dir: str = "data") -> QdrantClient:
    """Tries Qdrant Cloud first if env set, then local Docker Qdrant, then embedded."""
    url = os.environ.get("QDRANT_URL")
    api_key = os.environ.get("QDRANT_API_KEY")

    if url:
        try:
            client = QdrantClient(url=url, api_key=api_key, timeout=30)
            client.get_collections()
            print(f"[Ingest] Connected to Qdrant Cloud at {url[:35]}...")
            return client
        except Exception as e:
            print(f"[Ingest] Qdrant Cloud connection error: {e}")

    try:
        client = QdrantClient(host=host, port=port, timeout=5)
        client.get_collections()
        print(f"[Ingest] Connected to local Docker Qdrant at {host}:{port}")
        return client
    except Exception as e:
        storage_path = os.path.join(data_dir, "qdrant_storage")
        print(f"[Ingest] Local Qdrant unavailable ({e}). Using embedded storage at '{storage_path}'")
        return QdrantClient(path=storage_path)

def ingest_to_qdrant(data_dir: str = "data", host: str = "localhost", port: int = 6333):
    client = get_qdrant_client(host=host, port=port, data_dir=data_dir)
    collection_name = "nyaya_legal_and_schemes"

    print("Loading embedding model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    vector_size = 384

    # Re-create collection
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=qmodels.VectorParams(
            size=vector_size,
            distance=qmodels.Distance.COSINE
        )
    )
    print(f"Collection '{collection_name}' initialized.")

    # Create payload indices for fast filtered search
    for field in ["metadata.type", "metadata.state", "metadata.source"]:
        try:
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field,
                field_schema=qmodels.PayloadSchemaType.KEYWORD
            )
            print(f"Payload index created on '{field}'.")
        except Exception as e:
            print(f"Index notice on '{field}': {e}")

    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in data directory.")
        return

    points = []
    batch_size = 64
    total_points = 0

    # Ingest IPC Sections
    ipc_file = os.path.join(data_dir, "ipc_sections.csv")
    if os.path.exists(ipc_file):
        print(f"Processing IPC Sections from {ipc_file}...")
        df_ipc = pd.read_csv(ipc_file)
        batch_texts = []
        batch_metas = []

        for _, row in df_ipc.iterrows():
            sec = str(row.get('Section', '')).strip()
            offense = str(row.get('Offense', '')).strip()
            punishment = str(row.get('Punishment', 'None')).strip()
            desc = str(row.get('Description', '')).strip()

            content = f"Section {sec}: {offense}. Punishment: {punishment}.\n{desc}"
            metadata = {
                "source": "IPC/CrPC",
                "section": sec,
                "offense": offense,
                "punishment": punishment,
                "type": "legal",
            }
            batch_texts.append(content[:1500])
            batch_metas.append((content, metadata))

            if len(batch_texts) >= batch_size:
                vectors = embeddings.embed_documents(batch_texts)
                points = [
                    qmodels.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=v,
                        payload={"page_content": c, "metadata": m}
                    )
                    for v, (c, m) in zip(vectors, batch_metas)
                ]
                client.upsert(collection_name=collection_name, points=points)
                total_points += len(points)
                batch_texts = []
                batch_metas = []

        if batch_texts:
            vectors = embeddings.embed_documents(batch_texts)
            points = [
                qmodels.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=v,
                    payload={"page_content": c, "metadata": m}
                )
                for v, (c, m) in zip(vectors, batch_metas)
            ]
            client.upsert(collection_name=collection_name, points=points)
            total_points += len(points)

    # Ingest Schemes (structured_schemes.csv or updated_data.csv)
    scheme_file = os.path.join(data_dir, "structured_schemes.csv")
    if not os.path.exists(scheme_file):
        scheme_file = os.path.join(data_dir, "updated_data.csv")

    if os.path.exists(scheme_file):
        print(f"Processing Welfare Schemes from {scheme_file}...")
        df_schemes = pd.read_csv(scheme_file)
        batch_texts = []
        batch_metas = []

        for _, row in df_schemes.iterrows():
            name = str(row.get('scheme_name', '')).strip()
            cat = str(row.get('schemeCategory', '')).strip()
            details = str(row.get('details', '')).strip()
            benefits = str(row.get('benefits', '')).strip()
            eligibility = str(row.get('eligibility', '')).strip()
            state = str(row.get('state_name', row.get('state', row.get('level', 'All India')))).strip()
            gender = str(row.get('target_gender', row.get('gender', 'All'))).strip()
            caste = str(row.get('target_caste', row.get('caste', 'All'))).strip()

            content = (
                f"Scheme Name: {name}\n"
                f"Category: {cat}\n"
                f"State: {state}\n"
                f"Gender: {gender}\n"
                f"Caste: {caste}\n"
                f"Details: {details}\n"
                f"Benefits: {benefits}\n"
                f"Eligibility: {eligibility}"
            )
            metadata = {
                "source": "Government Scheme",
                "scheme_name": name,
                "category": cat,
                "state": state,
                "gender": gender,
                "caste": caste,
                "type": "scheme",
            }
            batch_texts.append(content[:1500])
            batch_metas.append((content, metadata))

            if len(batch_texts) >= batch_size:
                vectors = embeddings.embed_documents(batch_texts)
                points = [
                    qmodels.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=v,
                        payload={"page_content": c, "metadata": m}
                    )
                    for v, (c, m) in zip(vectors, batch_metas)
                ]
                client.upsert(collection_name=collection_name, points=points)
                total_points += len(points)
                batch_texts = []
                batch_metas = []

        if batch_texts:
            vectors = embeddings.embed_documents(batch_texts)
            points = [
                qmodels.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=v,
                    payload={"page_content": c, "metadata": m}
                )
                for v, (c, m) in zip(vectors, batch_metas)
            ]
            client.upsert(collection_name=collection_name, points=points)
            total_points += len(points)

    count_info = client.count(collection_name=collection_name)
    print(f" Successfully ingested {count_info.count} documents into Qdrant collection '{collection_name}'.")

if __name__ == "__main__":
    ingest_to_qdrant()
