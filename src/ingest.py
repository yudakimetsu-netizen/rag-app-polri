import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_documents(data_dir):
    documents = []
    # Loop melalui semua file di folder data
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(data_dir, filename)
            print(f"Memuat dokumen: {file_path}")
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
    
    print(f"Total halaman yang dimuat: {len(documents)}")
    print("Memotong dokumen menjadi chunks...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"Berhasil memproses {len(chunks)} chunks.")
    return chunks

if __name__ == "__main__":
    # Folder 'data' berisi file PDF Anda
    chunks = process_documents("data")
    
    if chunks:
        print("\nContoh isi chunk pertama:")
        print(chunks[0].page_content[:200])