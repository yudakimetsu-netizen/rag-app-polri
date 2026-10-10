import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from ingest import process_documents

# ==========================================
# 1. MEMUAT KONFIGURASI DARI FILE .env
# ==========================================
load_dotenv()

NEOSANTARA_API_KEY = os.getenv("NEOSANTARA_API_KEY")
BASE_URL = os.getenv("BASE_URL")

if not NEOSANTARA_API_KEY or not BASE_URL:
    raise ValueError("Pastikan NEOSANTARA_API_KEY dan BASE_URL sudah ada di file .env")

# ==========================================
# 2. FUNGSI BANTU
# ==========================================
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# ==========================================
# 3. MEMBANGUN RAG CHAIN
# ==========================================
def build_rag_chain():
    print("\n[1/4] Memproses dokumen PDF...")
    chunks = process_documents("data")

    print("\n[2/4] Membuat Vector Database (Menggunakan Embedding Lokal)...")
    # Menggunakan model embedding lokal yang gratis dan cepat
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = Chroma.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    print(f"      Vector Database berisi {len(chunks)} chunks.")

    print("\n[3/4] Menyiapkan LLM...")
    # LLM tetap menggunakan Neosantara
    llm = ChatOpenAI(
        model="amazon-nova-micro", # Pastikan nama model ini didukung Neosantara
        api_key=NEOSANTARA_API_KEY,
        base_url=BASE_URL,
        temperature=0
    )

    print("\n[4/4] Membangun RAG Chain...")
    system_prompt = (
        "Anda adalah asisten AI yang menjawab pertanyaan berdasarkan konteks yang diberikan. "
        "Gunakan potongan konteks berikut untuk menjawab pertanyaan. "
        "Jika Anda tidak tahu jawabannya, katakan saja Anda tidak tahu. "
        "Gunakan maksimal tiga kalimat dan jaga jawaban tetap ringkas.\n\n"
        "Konteks:\n{context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

# ==========================================
# 4. BLOK UTAMA
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("MEMBANGUN RAG PIPELINE")
    print("=" * 50)

    rag_chain = build_rag_chain()

    print("\n" + "=" * 50)
    print("RAG PIPELINE SIAP DIGUNAKAN")
    print("=" * 50)

    query = "Apa tujuan dari Peraturan Kepolisian Nomor 1 Tahun 2025?"
    print(f"\nPertanyaan: {query}")
    print("-" * 50)

    result = rag_chain.invoke(query)

    print("\nJAWABAN:")
    print(result)
    print("=" * 50)