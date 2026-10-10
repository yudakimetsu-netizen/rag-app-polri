def extractive_fallback(query: str, documents) -> str:
    """
    Fallback: pilih kalimat paling relevan dari dokumen
    jika LLM gagal atau tidak tersedia.
    """
    if not documents:
        return "Informasi tersebut tidak ditemukan dalam dokumen yang tersedia."

    query_words = set(query.lower().split())

    best_sentence = ""
    best_score = 0

    for doc in documents:
        sentences = doc.page_content.replace("\n", " ").split(". ")
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue

            sentence_words = set(sentence.lower().split())
            score = len(query_words & sentence_words)

            if score > best_score:
                best_score = score
                best_sentence = sentence

    if best_sentence:
        return f"(Fallback) {best_sentence}."
    return "Informasi tersebut tidak ditemukan dalam dokumen yang tersedia."