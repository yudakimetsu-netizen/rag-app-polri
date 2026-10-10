from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from src.retrieval.vector_store import get_store
from src.retrieval.reranker import build_reranker


def build_retriever(chunks, k_vector=10, k_bm25=10, top_n=5):
    """Build hybrid retriever + re-ranker (fungsi, bukan class)."""
    store = get_store()

    vector_retriever = store.as_retriever(
        search_kwargs={"k": k_vector}
    )

    bm25_retriever = BM25Retriever.from_documents(chunks, k=k_bm25)

    hybrid = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[0.6, 0.4],
    )

    return build_reranker(hybrid, top_n=top_n)


if __name__ == "__main__":
    from src.config import KNOWLEDGE_DIR
    from src.ingest.loaders import load_all_documents
    from src.ingest.chunker import chunk_documents

    print("Memuat dokumen...")
    docs = load_all_documents(KNOWLEDGE_DIR)
    chunks = chunk_documents(docs)
    print(f"Total: {len(chunks)} chunks")

    print("\nMembangun retriever...")
    retriever = build_retriever(chunks)

    query = "Apa syarat administrasi seleksi SBP?"
    print(f"\nQuery: {query}")
    results = retriever.invoke(query)
    print(f"Hasil: {len(results)} dokumen\n")

    for i, r in enumerate(results, 1):
        print(f"[{i}] {r.metadata.get('source')} hal.{r.metadata.get('page')}")
        print(f"    {r.page_content[:150]}...")
        print()