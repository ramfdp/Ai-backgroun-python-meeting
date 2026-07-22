from conversation_analysis import extract_timeline


def test_extract_timeline():
    text = """Laporan Notulensi Meeting Otomatis
[00:01] Pembicara 1: Pembukaan rapat.
[00:05] Pembicara 2: Kalimat panjang
yang berlanjut ke baris berikutnya.
---
KESIMPULAN:
Bagian ini tidak boleh ikut.
"""
    assert extract_timeline(text) == (
        "[00:01] Pembicara 1: Pembukaan rapat.\n"
        "[00:05] Pembicara 2: Kalimat panjang\n"
        "yang berlanjut ke baris berikutnya."
    )
