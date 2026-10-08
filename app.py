import streamlit as st
from src.rag_pipeline import build_rag_chain

# Konfigurasi halaman
st.set_page_config(
    page_title="RAG-Polri Q&A",
    page_icon="👮",
    layout="wide"
)

st.title("👮 Aplikasi Q&A Berbasis RAG")
st.caption("Seleksi Tahap 2 - BAGINFOPERS ROBNIKAR SSDM POLRI")

# Inisialisasi chat history di session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Inisialisasi RAG chain (hanya sekali saat aplikasi dimuat)
if "rag_chain" not in st.session_state:
    with st.spinner("Memuat model AI dan dokumen... Mohon tunggu (1-2 menit)."):
        st.session_state.rag_chain = build_rag_chain()
    st.success("Aplikasi siap digunakan!")

# Tampilkan chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input pengguna
if prompt := st.chat_input("Tanyakan sesuatu tentang dokumen..."):
    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Dapatkan jawaban dari RAG chain
    with st.chat_message("assistant"):
        with st.spinner("Mencari jawaban..."):
            response = st.session_state.rag_chain.invoke(prompt)
            st.markdown(response)
    
    # Simpan jawaban ke history
    st.session_state.messages.append({"role": "assistant", "content": response})