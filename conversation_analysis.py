from __future__ import annotations

from datetime import datetime
from pathlib import Path

from audio_recorder import STORAGE_FOLDERS, desktop_path
from conversation_analysis_prompt import CONVERSATION_ANALYSIS_PROMPT
from hermes_processor import run_hermes_prompt
from pdf_generator import save_to_pdf
from word_generator import export_to_word

def choose_txt_file():
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        return filedialog.askopenfilename(
            title="Pilih TXT transkrip meeting",
            parent=root,
            filetypes=[("Text Files", "*.txt")],
        )
    finally:
        root.destroy()


def analyze_with_hermes(conversation_path):
    print("Percakapan bertimestamp berhasil diekstrak. Menganalisis seluruh percakapan...")
    return run_hermes_prompt(CONVERSATION_ANALYSIS_PROMPT, conversation_path)


def analyze_txt_conversation(selected=None, analyzer=None, desktop=None, now=None):
    selected = selected or choose_txt_file()
    if not selected:
        print("Batal memilih file.")
        return None

    conversation_path = Path(selected)
    if not conversation_path.is_file():
        raise FileNotFoundError(conversation_path)
    if conversation_path.suffix.lower() != ".txt":
        raise ValueError("Format file harus .txt")
    if not conversation_path.read_text(encoding="utf-8").strip():
        raise ValueError("File transkrip kosong.")

    root = Path(desktop or desktop_path()) / "Hermes Transkrip"
    for folder in STORAGE_FOLDERS:
        (root / folder).mkdir(parents=True, exist_ok=True)

    stamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    name = f"Conversation_Analysis_{stamp}"
    analysis = (analyzer or analyze_with_hermes)(conversation_path)
    analysis_dir = root / "Analisis Lengkap"
    analysis_txt = analysis_dir / f"{name}.txt"
    analysis_pdf = analysis_dir / f"{name}.pdf"
    analysis_docx = analysis_dir / f"{name}.docx"
    analysis_txt.write_text(analysis, encoding="utf-8")
    save_to_pdf(analysis, filename=str(analysis_pdf))
    export_to_word(analysis, filename=str(analysis_docx))

    print(f"\nAnalisis selesai:\n-> {analysis_txt}\n-> {analysis_pdf}\n-> {analysis_docx}")
    return {
        "conversation_txt": conversation_path,
        "analysis_txt": analysis_txt,
        "analysis_pdf": analysis_pdf,
        "analysis_docx": analysis_docx,
    }


if __name__ == "__main__":
    try:
        analyze_txt_conversation()
    except Exception as error:
        print(f"[ERROR] Analisis TXT gagal: {error}")
