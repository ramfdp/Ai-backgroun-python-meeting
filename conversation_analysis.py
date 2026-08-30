from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader

from audio_recorder import STORAGE_FOLDERS, desktop_path
from conversation_analysis_prompt import CONVERSATION_ANALYSIS_PROMPT
from hermes_processor import run_hermes_prompt
from pdf_generator import save_to_pdf
from word_generator import export_to_word

TIMESTAMP = re.compile(r"^\[(?:\d{1,2}:)?\d{1,2}:\d{2}\]")
PDF_DECORATION = re.compile(r"^(Laporan Notulensi|Dibuat pada:|Halaman \d+)", re.I)


def extract_timeline(text):
    conversation = []
    started = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        marker = line.strip("*# ").upper()
        if TIMESTAMP.match(line):
            started = True
            conversation.append(line)
        elif started and (line == "---" or marker.startswith(("KESIMPULAN:", "ACTION ITEMS:"))):
            break
        elif started and line and not PDF_DECORATION.match(line):
            conversation.append(line)

    return "\n".join(conversation)


def choose_pdf_file():
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        return filedialog.askopenfilename(
            title="Pilih PDF transkrip meeting",
            parent=root,
            filetypes=[("PDF Files", "*.pdf")],
        )
    finally:
        root.destroy()


def analyze_with_hermes(conversation_path):
    print("Percakapan bertimestamp berhasil diekstrak. Menganalisis seluruh percakapan...")
    return run_hermes_prompt(CONVERSATION_ANALYSIS_PROMPT, conversation_path)


def analyze_pdf_conversation(selected=None, analyzer=None, desktop=None, now=None):
    selected = selected or choose_pdf_file()
    if not selected:
        print("Batal memilih file.")
        return None

    pdf_path = Path(selected)
    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Format file harus .pdf")

    pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(pdf_path).pages)
    conversation = extract_timeline(pdf_text)
    if not conversation:
        raise ValueError("Tidak ditemukan percakapan dengan format timestamp [MM:SS] di PDF.")

    root = Path(desktop or desktop_path()) / "Hermes Transkrip"
    for folder in STORAGE_FOLDERS:
        (root / folder).mkdir(parents=True, exist_ok=True)

    stamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    name = f"Conversation_Analysis_{stamp}"
    conversation_txt = root / "Transkrip" / f"{name}_conversation.txt"
    conversation_txt.write_text(conversation, encoding="utf-8")

    analysis = (analyzer or analyze_with_hermes)(conversation_txt)
    analysis_dir = root / "Analisis Lengkap"
    analysis_txt = analysis_dir / f"{name}.txt"
    analysis_pdf = analysis_dir / f"{name}.pdf"
    analysis_docx = analysis_dir / f"{name}.docx"
    analysis_txt.write_text(analysis, encoding="utf-8")
    save_to_pdf(analysis, filename=str(analysis_pdf))
    export_to_word(analysis, filename=str(analysis_docx))

    print(f"\nAnalisis selesai:\n-> {analysis_txt}\n-> {analysis_pdf}\n-> {analysis_docx}")
    print(f"Teks percakapan:\n-> {conversation_txt}")
    return {
        "conversation_txt": conversation_txt,
        "analysis_txt": analysis_txt,
        "analysis_pdf": analysis_pdf,
        "analysis_docx": analysis_docx,
    }


if __name__ == "__main__":
    try:
        analyze_pdf_conversation()
    except Exception as error:
        print(f"[ERROR] Analisis PDF gagal: {error}")
