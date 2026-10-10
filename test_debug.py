import sys
import os

print("=" * 60)
print("Python version:", sys.version)
print("Python exe:", sys.executable)
print("CWD:", os.getcwd())
print("=" * 60)

# TEST 1: Basic class tanpa import apapun
class Basic:
    def _init_(self):
        self.x = 1

b = Basic()
print("TEST 1 - Basic class _dict:", b.dict_)
print("TEST 1 - has x:", hasattr(b, 'x'))
print("=" * 60)

# TEST 2: Class setelah import HuggingFace
from langchain_community.embeddings import HuggingFaceEmbeddings

class AfterHF:
    def _init_(self):
        self.x = 2

a = AfterHF()
print("TEST 2 - After HF import, _dict:", a.dict_)
print("=" * 60)

# TEST 3: VectorStoreManager asli
sys.path.insert(0, os.getcwd())
from src.retrieval.vector_store import VectorStoreManager

v = VectorStoreManager()
print("TEST 3 - VSM _dict:", getattr(v, 'dict_', 'NO DICT'))
print("TEST 3 - VSM attrs:", [a for a in dir(v) if not a.startswith('__')])
print("TEST 3 - VSM type:", type(v))
print("=" * 60)
