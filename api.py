from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag_pipeline import build_rag_chain
import uvicorn

app = FastAPI(
    title="RAG-Polri API",
    description="API untuk aplikasi Q&A berbasis RAG",
    version="1.0.0"
)

# Inisialisasi RAG chain
rag_chain = build_rag_chain()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    try:
        result = rag_chain.invoke(request.question)
        return QueryResponse(answer=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Selamat datang di RAG-Polri API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)