from src.rag_chain import ask

queries = [
    "Apa syarat administrasi seleksi SBP?",
    "Apa tujuan Peraturan Kepolisian Nomor 1 Tahun 2025?",
    "Siapa presiden pertama Indonesia?",
]

for q in queries:
    print("=" * 60)
    print(f"Q: {q}")
    print("-" * 60)
    result = ask(q)
    print(f"A: {result['answer']}")
    print(f"Provider: {result['provider']}, Confidence: {result['confidence']}")
    print(f"Citations: {len(result['citations'])} sumber")
    for c in result["citations"][:3]:
        print(f"  - {c['source']} hal.{c['page']} ({c['authority']})")
    print()