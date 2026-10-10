import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ============================================
# BASE_DIR DETECTION (handle _file_ bug di Windows)
# ============================================
try:
    BASE_DIR = Path(_file_).resolve().parent.parent
except NameError:
    # Fallback untuk Windows Python bug / exec context
    cwd = Path(os.getcwd()).resolve()
    if (cwd / "src").exists():
        BASE_DIR = cwd
    elif (cwd.parent / "src").exists():
        BASE_DIR = cwd.parent
    else:
        BASE_DIR = cwd

print(f"[config] BASE_DIR = {BASE_DIR}")

# ============================================
# LOAD .env (dari BASE_DIR, atau fallback ke parent)
# ============================================
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()  # Coba dari cwd

# ============================================
# DATA & KNOWLEDGE DIRECTORIES (dengan auto-fallback)
# ============================================
DATA_DIR = BASE_DIR / "data"

# Cari KNOWLEDGE_DIR dengan beberapa kemungkinan lokasi
_knowledge_candidates = [
    DATA_DIR / "knowledge",       # Standard: data/knowledge/
    BASE_DIR / "knowledge",       # Fallback: knowledge/ di root (Streamlit Cloud)
]

KNOWLEDGE_DIR = None
for candidate in _knowledge_candidates:
    if candidate.exists():
        KNOWLEDGE_DIR = candidate
        break

# Kalau tidak ada satupun yang ada, default ke data/knowledge
if KNOWLEDGE_DIR is None:
    KNOWLEDGE_DIR = DATA_DIR / "knowledge"

INDEX_FILE = DATA_DIR / "index.json"
CHROMA_DIR = DATA_DIR / "chroma_db"

# ============================================
# PASTIKAN FOLDER ADA (untuk runtime)
# ============================================
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Hanya buat KNOWLEDGE_DIR kalau memang belum ada (jangan overwrite)
if not KNOWLEDGE_DIR.exists():
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

print(f"[config] KNOWLEDGE_DIR = {KNOWLEDGE_DIR}")
print(f"[config] CHROMA_DIR = {CHROMA_DIR}")

# ============================================
# API CONFIGURATION
# ============================================
NEOSANTARA_API_KEY = os.getenv("NEOSANTARA_API_KEY")
BASE_URL = os.getenv("BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL", "amazon-nova-micro")

# ============================================
# EMBEDDING CONFIGURATION
# ============================================
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# ============================================
# CHUNKING CONFIGURATION
# ============================================
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

# ============================================
# AUTHORITY RANKING
# ============================================
AUTHORITY_RANKS = {
    "verified_original": 3,      # PDF resmi asli
    "verified_regulation": 2,    # Peraturan (Perpol)
    "structured_guidance": 1,    # Breakdown/ringkasan
    "unknown": 0,
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


# ============================================
# VALIDASI (non-fatal, hanya warning)
# ============================================
def validate_config(raise_error: bool = False) -> bool:
    """
    Validasi konfigurasi. Default: hanya print warning, tidak raise.
    Set raise_error=True kalau mau raise ValueError.
    """
    issues = []
    if not NEOSANTARA_API_KEY:
        issues.append("NEOSANTARA_API_KEY tidak ada di .env")
    if not BASE_URL:
        issues.append("BASE_URL tidak ada di .env")
    if not KNOWLEDGE_DIR.exists():
        issues.append(f"KNOWLEDGE_DIR tidak ada: {KNOWLEDGE_DIR}")
    elif not any(KNOWLEDGE_DIR.iterdir()):
        issues.append(f"KNOWLEDGE_DIR kosong: {KNOWLEDGE_DIR}")

    if issues:
        for issue in issues:
            print(f"[config] WARNING: {issue}")
        if raise_error:
            raise ValueError("; ".join(issues))
        return False
    return True


# ============================================
# DEBUG INFO (dijalankan kalau file ini di-run langsung)
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("KONFIGURASI RAG-POLRI")
    print("=" * 60)
    print(f"BASE_DIR       : {BASE_DIR}")
    print(f"DATA_DIR       : {DATA_DIR}")
    print(f"KNOWLEDGE_DIR  : {KNOWLEDGE_DIR}")
    print(f"INDEX_FILE     : {INDEX_FILE}")
    print(f"CHROMA_DIR     : {CHROMA_DIR}")
    print(f"LLM Model      : {LLM_MODEL}")
    print(f"Embedding      : {EMBEDDING_MODEL} ({EMBEDDING_DIMENSION} dim)")
    print(f"Chunk size     : {CHUNK_SIZE} (overlap: {CHUNK_OVERLAP})")
    print(f"API Key        : {'OK' if NEOSANTARA_API_KEY else 'MISSING'}")
    print(f"Base URL       : {BASE_URL if BASE_URL else 'MISSING'}")

    # Cek isi knowledge dir
    if KNOWLEDGE_DIR.exists():
        files = list(KNOWLEDGE_DIR.iterdir())
        print(f"Isi KNOWLEDGE  : {len(files)} file")
        for f in files:
            print(f"  - {f.name}")

    print("=" * 60)
    if validate_config():
        print("STATUS: OK - Siap digunakan")
    else:
        print("STATUS: ADA WARNING (lihat di atas)")
    print("=" * 60)