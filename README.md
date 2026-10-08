# Aplikasi Q&A Berbasis RAG 

## 1. Penjelasan Aplikasi
Aplikasi ini adalah sistem Question and Answer (QnA) berbasis Retrieval-Augmented Generation (RAG) yang dirancang untuk menjawab pertanyaan pengguna berdasarkan dokumen/knowledge base yang diunggah. Aplikasi ini memiliki antarmuka sederhana berupa chat history, kotak teks, dan tombol kirim.

## 2. Techstack yang Digunakan
- *Bahasa:* Python 3.14
- *Framework UI:* Streamlit
- *Orkestrasi RAG:* LangChain (LCEL)
- *Vector Database:* ChromaDB
- *Embedding Model:* all-MiniLM-L6-v2 (HuggingFace, lokal)
- *LLM:* Amazon Nova Micro (via Neosantara Gateway)
- *Dokumen:* PDF (2 file)

## 3. Arsitektur / Workflow RAG
1. *Ingestion:* Dokumen PDF di-load dan di-parsing menggunakan PyPDFLoader.
2. *Chunking:* Teks dipecah menjadi potongan kecil (chunk) menggunakan RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200).
3. *Embedding:* Chunk diubah menjadi vektor menggunakan model all-MiniLM-L6-v2 yang berjalan secara lokal.
4. *Vector DB:* Vektor disimpan di ChromaDB.
5. *Retrieval:* Query pengguna di-embed dan dicari kemiripan (similarity search) di Vector DB (top-3).
6. *Generation:* Konteks yang relevan + Query dikirim ke LLM untuk menghasilkan jawaban.

## 4. Petunjuk Instalasi
1. Clone repository ini.
2. Buat virtual environment: python -m venv venv
3. Aktifkan venv: venv\Scripts\activate (Windows) atau source venv/bin/activate (Linux/Mac).
4. Install dependensi: pip install -r requirements.txt
5. Buat file .env dan isi:
6. Jalankan aplikasi: python -m streamlit run app.py