from src.config import KNOWLEDGE_DIR
from src.ingest.loaders import load_all_documents
from src.ingest.chunker import chunk_documents

print("Loading documents...")
docs = load_all_documents(KNOWLEDGE_DIR)
print(f"Total halaman: {len(docs)}")

print("\nChunking...")
chunks = chunk_documents(docs)
print(f"Total chunks: {len(chunks)}")

# Hapus Chroma lama
import shutil
from pathlib import Path
chroma_dir = Path("data/chroma_db")
if chroma_dir.exists():
    shutil.rmtree(chroma_dir)
    print("\nChroma lama dihapus.")

# Build vector store
print("\nBuilding vector store...")
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from src.config import EMBEDDING_MODEL

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vectorstore = Chroma.from_documents(
    chunks,
    embeddings,
    persist_directory=str(chroma_dir),
    collection_name="rag_polri"
)

print(f"\nSELESAI")
print(f"Total file: {len(set(c.metadata['source'] for c in chunks))}")
print(f"Total chunks: {len(chunks)}")
print(f"Vector store tersimpan: {chroma_dir}")