def build_citations(documents):
    """Bentuk citation terstruktur dari dokumen hasil retrieval."""
    citations = []
    seen = set()

    for doc in documents:
        meta = doc.metadata
        chunk_id = meta.get("chunk_id", "unknown")

        if chunk_id in seen:
            continue
        seen.add(chunk_id)

        citations.append({
            "source": meta.get("source", "unknown"),
            "page": meta.get("page", 1),
            "chunk_index": meta.get("chunk_index", 0),
            "authority": meta.get("authority", "unknown"),
            "authority_rank": meta.get("authority_rank", 0),
            "preview": doc.page_content[:150] + "...",
        })

    return citations