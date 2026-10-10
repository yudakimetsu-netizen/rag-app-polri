from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = (
    "Anda adalah asisten AI yang menjawab pertanyaan berdasarkan konteks dokumen resmi. "
    "Gunakan HANYA informasi dari konteks di bawah ini. "
    "Jika jawaban tidak ditemukan dalam konteks, katakan dengan jujur: "
    "'Informasi tersebut tidak ditemukan dalam dokumen yang tersedia.' "
    "Jangan menambahkan pengetahuan dari luar konteks. "
    "Jawablah dengan ringkas, jelas, dan terstruktur. "
    "Jika memungkinkan, sebutkan sumber/halaman.\n\n"
    "Konteks:\n{context}"
)


def get_rag_prompt():
    """Build RAG prompt template."""
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])