import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from ingest import process_documents

load_dotenv()
NEOSANTARA_API_KEY = os.getenv("NEOSANTARA_API_KEY")
BASE_URL = os.getenv("BASE_URL")


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_advanced_rag():
    print("[1/4] Memproses dokumen PDF...")
    chunks = process_documents("data")

    print("[2/4] Membuat Vector Database...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(chunks, embeddings)

    # Filter: hanya cari di dokumen PENGUMUMAN SBP
    base_retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 20,
            "filter": {"source_file": "PENGUMUMAN SBP TA 2027.pdf"}
        }
    )

    print("[3/4] Menambahkan Re-ranker (Cross-Encoder)...")
    cross_encoder = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
    reranker = CrossEncoderReranker(model=cross_encoder, top_n=5)

    final_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=base_retriever
    )

    print("[4/4] Menyiapkan LLM...")
    llm = ChatOpenAI(
        model="amazon-nova-micro",
        api_key=NEOSANTARA_API_KEY,
        base_url=BASE_URL,
        temperature=0
    )

    system_prompt = (
        "Anda adalah asisten AI yang menjawab pertanyaan berdasarkan konteks dokumen. "
        "Gunakan informasi dari konteks di bawah ini untuk menjawab. "
        "Jika informasi benar-benar tidak ada, katakan dengan jujur. "
        "Jawablah dengan ringkas, jelas, dan terstruktur.\n\n"
        "Konteks:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    rag_chain = (
        {"context": final_retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


if __name__ == "__main__":
    print("=" * 50)
    print("MEMBANGUN ADVANCED RAG (Vector + Re-ranking)")
    print("=" * 50)

    rag_chain = build_advanced_rag()

    query = "Apa syarat administrasi untuk mengikuti seleksi SBP?"
    print(f"\nPertanyaan: {query}\n")

    result = rag_chain.invoke(query)
    print("JAWABAN:")
    print(result)