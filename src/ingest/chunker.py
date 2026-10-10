import hashlib
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, detect_authority, AUTHORITY_RANKS

def compute_hash(text: str) -> str:
    """Hash SHA-256 dari teks."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

def normalize_text(text: str) -> str:
    """Normalisasi whitespace dan buang karakter NUL."""
    text = text.replace("\x00", "")
    # Rapikan whitespace berlebih
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)

def chunk_documents(documents: list[Document]) -> list[Document]:
    """Potong dokumen menjadi chunk dengan metadata lengkap."""
    print(f"Memotong {len(documents)} halaman menjadi chunks...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = []
    for doc in documents:
        # Normalisasi
        text = normalize_text(doc.page_content)
        if not text:
            continue
        
        source = doc.metadata.get("source", "unknown")
        authority = detect_authority(source)
        authority_rank = AUTHORITY_RANKS.get(authority, 0)
        
        # Split
        sub_chunks = splitter.split_text(text)
        
        for i, chunk_text in enumerate(sub_chunks):
            chunk_meta = {
                **doc.metadata,
                "chunk_id": f"{source}::{compute_hash(chunk_text)}",
                "chunk_index": i,
                "total_chunks": len(sub_chunks),
                "authority": authority,
                "authority_rank": authority_rank,
                "content_hash": compute_hash(chunk_text),
            }
            chunks.append(Document(page_content=chunk_text, metadata=chunk_meta))
    
    print(f"Selesai: {len(chunks)} chunks")
    return chunks


if __name__ == "__main__":
    from src.config import KNOWLEDGE_DIR
    from src.ingest.loaders import load_all_documents
    
    docs = load_all_documents(KNOWLEDGE_DIR)
    chunks = chunk_documents(docs)
    
    if chunks:
        print("\nContoh chunk pertama:")
        print(f"  Sumber    : {chunks[0].metadata['source']}")
        print(f"  Authority : {chunks[0].metadata['authority']}")
        print(f"  Rank      : {chunks[0].metadata['authority_rank']}")
        print(f"  Content   : {chunks[0].page_content[:150]}...")