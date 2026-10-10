import json
from datetime import datetime
from pathlib import Path
from src.config import (
    KNOWLEDGE_DIR, INDEX_FILE, CHROMA_DIR, EMBEDDING_MODEL
)
from src.ingest.loaders import load_all_documents
from src.ingest.chunker import chunk_documents

def build_index(save_json: bool = True):
    """Build index dari semua dokumen di knowledge dir."""
    print("=" * 60)
    print("BUILD INDEX RAG-POLRI")
    print("=" * 60)
    
    # 1. Load documents
    print("\n[1/3] Loading documents...")
    documents = load_all_documents(KNOWLEDGE_DIR)
    if not documents:
        print("ERROR: Tidak ada dokumen yang dimuat!")
        return None
    
    # 2. Chunking
    print("\n[2/3] Chunking...")
    chunks = chunk_documents(documents)
    
    # 3. Build Vector Store
    print("\n[3/3] Building Vector Store...")
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # Hapus chroma lama jika ada
    if CHROMA_DIR.exists():
        import shutil
        shutil.rmtree(CHROMA_DIR)
    
    vectorstore = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="rag_polri"
    )
    print(f"Vector store tersimpan di: {CHROMA_DIR}")
    
    # 4. Save index.json (snapshot)
    if save_json:
        snapshot = {
            "built_at": datetime.now().isoformat(),
            "total_documents": len(documents),
            "total_chunks": len(chunks),
            "sources": sorted(set(c.metadata["source"] for c in chunks)),
            "chunks": [
                {
                    "chunk_id": c.metadata["chunk_id"],
                    "source": c.metadata["source"],
                    "page": c.metadata.get("page", 1),
                    "chunk_index": c.metadata["chunk_index"],
                    "authority": c.metadata["authority"],
                    "authority_rank": c.metadata["authority_rank"],
                    "content_hash": c.metadata["content_hash"],
                    "preview": c.page_content[:200],
                }
                for c in chunks
            ]
        }
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        print(f"Snapshot tersimpan: {INDEX_FILE}")
    
    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)
    print(f"Total file  : {len(set(c.metadata['source'] for c in chunks))}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Embedding   : {EMBEDDING_MODEL}")
    
    return vectorstore


def load_existing_index():
    """Load vector store yang sudah ada."""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    
    if not CHROMA_DIR.exists():
        print("Chroma tidak ditemukan, silakan build index dulu.")
        return None
    
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory=str(CHROMA_DIR),
        collection_name="rag_polri",
        embedding_function=embeddings
    )
    return vectorstore


if __name__ == "__main__":
    build_index()