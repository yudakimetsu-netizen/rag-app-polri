import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Deteksi BASE_DIR dengan fallback
try:
    BASE_DIR = Path(_file_).resolve().parent.parent
except NameError:
    # Fallback: cari folder root proyek dari cwd
    cwd = Path(os.getcwd()).resolve()
    # Cari folder yang punya subfolder 'src'
    if (cwd / "src").exists():
        BASE_DIR = cwd
    elif (cwd.parent / "src").exists():
        BASE_DIR = cwd.parent
    else:
        BASE_DIR = cwd  # fallback terakhir

print(f"[config] BASE_DIR = {BASE_DIR}")

load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
INDEX_FILE = DATA_DIR / "index.json"
CHROMA_DIR = DATA_DIR / "chroma_db"

# Pastikan folder ada
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# API CONFIGURATION
# ==========================================
NEOSANTARA_API_KEY = os.getenv("NEOSANTARA_API_KEY")
BASE_URL = os.getenv("BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL", "amazon-nova-micro")

# ==========================================
# EMBEDDING CONFIGURATION
# ==========================================
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# ==========================================
# CHUNKING CONFIGURATION
# ==========================================
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

# ==========================================
# AUTHORITY RANKING
# ==========================================
# Semakin tinggi rank, semakin otoritatif sumber
AUTHORITY_RANKS = {
    "verified_original": 3,      # PDF resmi asli
    "verified_regulation": 2,    # Peraturan (Perpol)
    "structured_guidance": 1,    # Breakdown/ringkasan
    "unknown": 0
}

def detect_authority(filename: str) -> str:
    """Deteksi tingkat otoritas berdasarkan nama file."""
    name_lower = filename.lower()
    if "perpol" in name_lower or "peraturan" in name_lower:
        return "verified_regulation"
    if "pengumuman" in name_lower or "resmi" in name_lower:
        return "verified_original"
    if "breakdown" in name_lower or "ringkasan" in name_lower:
        return "structured_guidance"
    return "unknown"

# ==========================================
# VALIDASI
# ==========================================
def validate_config():
    if not NEOSANTARA_API_KEY:
        raise ValueError("NEOSANTARA_API_KEY tidak ada di .env")
    if not BASE_URL:
        raise ValueError("BASE_URL tidak ada di .env")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("KONFIGURASI RAG-POLRI")
    print("=" * 50)
    print(f"Knowledge dir : {KNOWLEDGE_DIR}")
    print(f"Index file    : {INDEX_FILE}")
    print(f"Chroma dir    : {CHROMA_DIR}")
    print(f"LLM Model     : {LLM_MODEL}")
    print(f"Embedding     : {EMBEDDING_MODEL} ({EMBEDDING_DIMENSION} dim)")
    print(f"Chunk size    : {CHUNK_SIZE} (overlap: {CHUNK_OVERLAP})")
    try:
        validate_config()
        print("API Config    : OK")
    except ValueError as e:
        print(f"API Config    : ERROR - {e}")