# Dokumentasi API - RAG-Polri

## Base URL
http://localhost:8000

## Endpoints

### 1. GET /
Cek status API.

*Response:*
\\\`json
{"message": "Selamat datang di RAG-Polri API"}
\\\`

### 2. POST /ask
Kirim pertanyaan ke RAG dan dapatkan jawaban.

*Request Body:*
\\\`json
{
  "question": "Apa syarat administrasi untuk mengikuti seleksi SBP?"
}
\\\`

*Response:*
\\\`json
{
  "answer": "Syarat administrasi untuk mengikuti seleksi SBP antara lain..."
}
\\\`

## Tools untuk Testing
- Apilog
- Postman
- Insomnia
- Swagger UI (http://localhost:8000/docs)