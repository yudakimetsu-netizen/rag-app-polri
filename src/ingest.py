import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_documents(data_dir):
    documents = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(data_dir, filename)
            print(f"Memuat dokumen: {file_path}")
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            # Tambahkan metadata nama file ke setiap dokumen
            for doc in docs:
                doc.metadata["source_file"] = filename
            documents.extend(docs)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Berhasil memproses {len(chunks)} chunks.")
    return chunks