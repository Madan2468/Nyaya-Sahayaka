import os
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

def ingest_data():
    """
    Reads CSVs placed in the data/ folder, embeds them using IndicBERT,
    and saves the FAISS index to disk.
    """
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in {data_dir}/.")
        return
        
    all_docs = []
    
    for file in csv_files:
        print(f"Loading {file}...")
        df = pd.read_csv(os.path.join(data_dir, file))
        
        # Data Mappings based on real datasets
        if 'Offense' in df.columns and 'Section' in df.columns:
            # IPC/CrPC Dataset mapping
            for _, row in df.iterrows():
                content = f"Section {row.get('Section', '')}: {row.get('Offense', '')}. Punishment: {row.get('Punishment', 'None')}."
                metadata = {"source": "IPC/CrPC", "section": str(row.get('Section', '')), "type": "legal"}
                all_docs.append(Document(page_content=content, metadata=metadata))
        elif 'scheme_name' in df.columns and 'details' in df.columns:
            # New mapping for updated_data.csv (Government Schemes)
            for _, row in df.iterrows():
                content = f"Scheme Name: {row.get('scheme_name', '')}\nCategory: {row.get('schemeCategory', '')}\nDetails: {row.get('details', '')}\nBenefits: {row.get('benefits', '')}\nEligibility: {row.get('eligibility', '')}"
                metadata = {"source": "Government Scheme", "state": str(row.get('level', '')), "type": "scheme"}
                all_docs.append(Document(page_content=content, metadata=metadata))
        elif 'Scheme Name' in df.columns and 'Description' in df.columns:
            # Old mapping just in case
            for _, row in df.iterrows():
                content = f"Scheme Name: {row.get('Scheme Name', '')}\nDescription: {row.get('Description', '')}"
                metadata = {"source": "Government Scheme", "state": str(row.get('Central/State Govt.', '')), "type": "scheme"}
                all_docs.append(Document(page_content=content, metadata=metadata))
        elif 'content' in df.columns:
            loader = DataFrameLoader(df, page_content_column="content")
            all_docs.extend(loader.load())
        else:
            print(f"Skipping {file} - Unrecognized column structure.")
            continue
            
    if not all_docs:
        print("No documents were loaded. Check CSV format.")
        return
        
    print(f"Loaded {len(all_docs)} documents across dataset. Generating embeddings...")
    # Switched to a public multilingual model since ai4bharat requires HF token
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    print("Building FAISS vector database. This may take a few minutes...")
    vector_store = FAISS.from_documents(all_docs, embeddings)
    
    output_path = os.path.join(data_dir, "faiss_index")
    vector_store.save_local(output_path)
    print(f"Successfully saved AI search index to {output_path}")

if __name__ == "__main__":
    ingest_data()
