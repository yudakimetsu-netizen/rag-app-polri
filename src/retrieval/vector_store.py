from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config import CHROMA_DIR, EMBEDDING_MODEL

# ============================================
# STATE (disimpan sebagai module-level variable)
# ============================================
_embeddings = None
_store = None


def _get_embeddings():
    """Lazy load embeddings (cached)."""
    global _embeddings
    if _embeddings is None:
        print("[vector_store] Loading embeddings...")
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        print("[vector_store] Embeddings loaded.")
    return _embeddings


def get_store():
    """Ambil (atau load) Chroma vector store."""
    global _store
    if _store is None:
        if not CHROMA_DIR.exists():
            raise FileNotFoundError(
                f"Chroma tidak ditemukan di {CHROMA_DIR}. Jalankan build_index dulu."
            )
        print("[vector_store] Loading Chroma...")
        _store = Chroma(
            persist_directory=str(CHROMA_DIR),
            collection_name="rag_polri",
            embedding_function=_get_embeddings(),
        )
        print("[vector_store] Chroma loaded.")
    return _store


def get_stats():
    """Statistik vector store."""
    try:
        store = get_store()
        count = store._collection.count()
        return {"status": "ok", "total_chunks": count, "dimension": 384}
    except Exception as e:
        return {"status": "error", "message": str(e)}