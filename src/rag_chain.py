# RAG Chain - Final Version (tanpa filter, pakai hybrid retriever langsung)

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.config import KNOWLEDGE_DIR, CHROMA_DIR
from src.ingest.loaders import load_all_documents
from src.ingest.chunker import chunk_documents
from src.retrieval.hybrid import build_retriever
from src.generation.llm import get_llm
from src.generation.prompts import get_rag_prompt
from src.generation.domain_gate import is_domain_question
from src.citation import build_citations
from src.fallback import extractive_fallback

# STATE
_retriever = None
_initialized = False


def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def _auto_build_chroma():
    from pathlib import Path
    chroma_path = Path(CHROMA_DIR)
    if chroma_path.exists() and any(chroma_path.iterdir()):
        return
    print("[rag_chain] Auto-build ChromaDB...")
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    from src.config import EMBEDDING_MODEL
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    Chroma.from_documents(
        _chunks, embeddings,
        persist_directory=str(chroma_path),
        collection_name="rag_polri",
    )
    print("[rag_chain] ChromaDB siap.")


def _ensure_initialized():
    global _retriever, _initialized, _chunks
    if _initialized:
        return
    print("[rag_chain] Init...")
    docs = load_all_documents(KNOWLEDGE_DIR)
    if not docs:
        raise RuntimeError("Tidak ada dokumen di knowledge dir")
    _chunks = chunk_documents(docs)
    print(f"[rag_chain] Total chunks: {len(_chunks)}")
    _auto_build_chroma()
    _retriever = build_retriever(_chunks)
    print("[rag_chain] Retriever siap.")
    _initialized = True


def ask(query):
    # 1. Domain gate
    if not is_domain_question(query):
        return {
            "answer": "Maaf, pertanyaan Anda di luar domain dokumen yang saya miliki.",
            "citations": [],
            "provider": "domain-gate",
            "confidence": 0.0,
        }

    # 2. Init
    _ensure_initialized()

    # 3. Retrieval (langsung pakai hybrid retriever, tanpa filter)
    print(f"[rag_chain] Query: {query[:60]}...")
    docs = _retriever.invoke(query)
    print(f"[rag_chain] Retrieved {len(docs)} docs")

    if not docs:
        return {
            "answer": "Informasi tersebut tidak ditemukan dalam dokumen yang tersedia.",
            "citations": [],
            "provider": "no-docs",
            "confidence": 0.0,
        }

    # 4. Generation
    try:
        llm = get_llm()
        prompt = get_rag_prompt()
        chain = (
            {
                "context": lambda x: _format_docs(docs),
                "input": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        answer = chain.invoke(query)
        provider = "neosantara"
    except Exception as e:
        print(f"[rag_chain] LLM error: {e}")
        answer = extractive_fallback(query, docs)
        provider = "fallback"

    # 5. Citations
    citations = build_citations(docs)

    return {
        "answer": answer,
        "citations": citations,
        "provider": provider,
        "confidence": 0.85 if provider == "neosantara" else 0.4,
    }