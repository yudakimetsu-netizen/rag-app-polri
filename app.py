import streamlit as st
from src.rag_chain import ask

st.set_page_config(
    page_title="RAG-Polri Chatbot",
    page_icon="👮",
    layout="wide",
)

st.title("👮 RAG-Polri Chatbot")
st.caption("Seleksi Tahap 2 - BAGINFOPERS ROBNIKAR SSDM POLRI")

# Sidebar info
with st.sidebar:
    st.header("ℹ️ Tentang Aplikasi")
    st.markdown("""
    Chatbot berbasis *RAG (Retrieval-Augmented Generation)* yang menjawab 
    pertanyaan berdasarkan dokumen resmi:
    - 📄 PENGUMUMAN SBP TA 2027
    - 📄 PERPOL NO 1 TAHUN 2025
    
    *Techstack:*
    - LangChain + ChromaDB
    - HuggingFace Embeddings
    - Amazon Nova Micro (via Neosantara)
    - Hybrid Search + Re-ranking
    """)
    st.divider()
    st.caption("© 2026 - BAGINFOPERS ROBNIKAR SSDM POLRI")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            with st.expander(f"📚 Sumber Jawaban ({len(msg['citations'])})"):
                for c in msg["citations"]:
                    st.markdown(f"- *{c['source']}* (hal. {c['page']}) — {c['authority']}")
                    st.caption(f"{c['preview'][:150]}...")

# Input
if prompt := st.chat_input("Tanyakan sesuatu tentang SBP atau Perpol..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Mencari jawaban..."):
            try:
                result = ask(prompt)
                answer = result["answer"]
                citations = result["citations"]
                provider = result["provider"]
                confidence = result["confidence"]

                st.markdown(answer)

                if citations:
                    with st.expander(f"📚 Sumber Jawaban ({len(citations)})"):
                        for c in citations:
                            st.markdown(f"- *{c['source']}* (hal. {c['page']}) — {c['authority']}")
                            st.caption(f"{c['preview'][:150]}...")

                col1, col2 = st.columns(2)
                col1.caption(f"🤖 Provider: {provider}")
                col2.caption(f"📊 Confidence: {confidence}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "citations": citations,
                })
            except Exception as e:
                st.error(f"Error: {e}")