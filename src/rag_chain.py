from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.config import KNOWLEDGE_DIR
from src.ingest.loaders import load_all_documents
from src.ingest.chunker import chunk_documents
from src.retrieval.hybrid import build_retriever
from src.generation.llm import get_llm
from src.generation.prompts import get_rag_prompt
from src.generation.domain_gate import is_domain_question
from src.citation import build_citations
from src.fallback import extractive_fallback

# ============================================
# STATE
# ============================================
_retriever = None
_chunks = None
_sources = None


def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def _ensure_retriever():
    """Lazy build retriever (cached)."""
    global _retriever, _chunks, _sources
    if _retriever is None:
        print("[rag_chain] Memuat dokumen & membangun retriever...")
        docs = load_all_documents(KNOWLEDGE_DIR)
        _chunks = chunk_documents(docs)
        _retriever = build_retriever(_chunks)

        # Cache daftar source yang ada di ChromaDB
        from src.retrieval.vector_store import get_store
        store = get_store()
        results = store.get(limit=10000)
        _sources = list(set(m.get("source", "") for m in results["metadatas"]))
        print(f"[rag_chain] Retriever siap dengan {len(_chunks)} chunks.")
        print(f"[rag_chain] Sumber tersedia: {_sources}")
    return _retriever


def _detect_filter(query: str):
    """Deteksi dokumen mana yang harus difilter (auto-detect nama file)."""
    if _sources is None:
        return None

    q_lower = query.lower()

    # Kata kunci untuk SBP (PENGUMUMAN)
    sbp_keywords = [
        "sbp", "seleksi", "tamtama", "bintara", "pendaftaran",
        "syarat administrasi", "persyaratan", "dokumen pendaftaran",
        "jadwal seleksi", "tahapan seleksi", "panpus", "panda",
        "pasfoto", "skhp", "sipk", "ijazah", "akreditasi",
    ]
    # Kata kunci untuk PERPOL (penilaian kinerja)
    perpol_keywords = [
        "penilaian kinerja", "sipk online", "litcatpers", "e-rohani",
        "e-mental", "pka", "faktor spesifik", "faktor generik",
        "kontrak kerja", "tugas lain", "penghargaan",
    ]

    # Cari file SBP
    if any(kw in q_lower for kw in sbp_keywords):
        for src in _sources:
            if "PENGUMUMAN" in src.upper() and "SBP" in src.upper():
                return {"source": src}

    # Cari file PERPOL
    if any(kw in q_lower for kw in perpol_keywords):
        for src in _sources:
            if "PERPOL" in src.upper():
                return {"source": src}

    return None


def ask(query: str) -> dict:
    """Endpoint utama: tanya ke RAG, dapatkan jawaban + citations."""
    # 1. Domain gate
    if not is_domain_question(query):
        return {
            "answer": "Maaf, pertanyaan Anda di luar domain dokumen yang saya miliki.",
            "citations": [],
            "provider": "domain-gate",
            "confidence": 0.0,
        }

    # 2. Retrieval dengan filter otomatis
    retriever = _ensure_retriever()
    filter_meta = _detect_filter(query)
    print(f"[rag_chain] Filter: {filter_meta}")

    if filter_meta:
        from src.retrieval.vector_store import get_store
        store = get_store()
        filtered_retriever = store.as_retriever(
            search_kwargs={"k": 10, "filter": filter_meta}
        )
        docs = filtered_retriever.invoke(query)
    else:
        docs = retriever.invoke(query)

    if not docs:
        return {
            "answer": "Informasi tersebut tidak ditemukan dalam dokumen yang tersedia.",
            "citations": [],
            "provider": "no-docs",
            "confidence": 0.0,
        }

    # 3. Generation
    try:
        llm = get_llm()
        prompt = get_rag_prompt()

        chain = (
            {"context": lambda x: _format_docs(docs), "input": RunnablePassthrough()}
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

    # 4. Citations
    citations = build_citations(docs)

    return {
        "answer": answer,
        "citations": citations,
        "provider": provider,
        "confidence": 0.85 if provider == "neosantara" else 0.4,
    }