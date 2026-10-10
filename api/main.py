from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.rag_chain import ask
from src.retrieval.vector_store import get_stats

app = FastAPI(
    title="RAG-Polri API - Advanced",
    description="API RAG kelas menengah dengan domain gate, citation, dan fallback",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


class Citation(BaseModel):
    source: str
    page: int
    authority: str
    preview: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    provider: str
    confidence: float


@app.get("/api/health")
def health():
    """Health check."""
    stats = get_stats()
    return {
        "status": stats.get("status", "unknown"),
        "vector_store": stats,
        "version": "2.0.0",
    }


@app.get("/api/stats")
def stats():
    """Statistik RAG."""
    return get_stats()


@app.post("/api/chat", response_model=AskResponse)
def chat(req: AskRequest):
    """Endpoint utama: tanya ke RAG."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question tidak boleh kosong.")
    try:
        result = ask(req.question)
        return AskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "RAG-Polri API v2.0", "docs": "/docs"}