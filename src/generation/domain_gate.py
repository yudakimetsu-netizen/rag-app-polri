DOMAIN_KEYWORDS = [
    "sbp", "sekolah bintara", "tamtama", "bintara", "polri", "polisi",
    "perpol", "peraturan", "kepolisian", "seleksi", "pendidikan",
    "persyaratan", "syarat", "administrasi", "dokumen", "pendaftaran",
    "pangkat", "mddp", "penilaian", "kinerja", "sipk", "litcatpers",
    "panpus", "panda", "subpanpus", "jadwal", "tahapan", "kelulusan",
    "mdp", "abrip", "bharaka", "akademik", "ijazah", "skhp",
    "kesehatan", "jasmani", "psikologi", "tkp", "tkk", "cat",
]


def is_domain_question(query: str) -> bool:
    """Cek apakah pertanyaan dalam domain SBP/Perpol."""
    q_lower = query.lower()
    return any(kw in q_lower for kw in DOMAIN_KEYWORDS)


if __name__ == "__main__":
    tests = [
        "Apa syarat administrasi seleksi SBP?",
        "Apa tujuan Peraturan Kepolisian Nomor 1 Tahun 2025?",
        "Siapa presiden pertama Indonesia?",
        "Bagaimana cara membuat kue?",
    ]
    for t in tests:
        print(f"[{'OK ' if is_domain_question(t) else 'SKIP'}] {t}")