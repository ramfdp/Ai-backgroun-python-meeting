import os
import re
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

from pypdf import PdfReader

from conversation_analysis_prompt import CONVERSATION_ANALYSIS_PROMPT
from gemini_processor import _call_gemini
from pdf_generator import save_to_pdf
from word_generator import export_to_word


TIMESTAMP = re.compile(r"^\[(?:\d{1,2}:)?\d{1,2}:\d{2}\]")
PDF_DECORATION = re.compile(r"^(Laporan Notulensi|Dibuat pada:|Halaman \d+)", re.I)


def extract_timeline(text):
    conversation = []
    started = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if TIMESTAMP.match(line):
            started = True
            conversation.append(line)
        elif started and (line == "---" or line.upper().startswith(("KESIMPULAN:", "ACTION ITEMS:"))):
            break
        elif started and line and not PDF_DECORATION.match(line):
            conversation.append(line)

    return "\n".join(conversation)


def analyze_pdf_conversation():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    pdf_path = filedialog.askopenfilename(
        title="Pilih PDF transkrip meeting",
        parent=root,
        filetypes=[("PDF Files", "*.pdf")],
    )
    root.destroy()

    if not pdf_path:
        print("Batal memilih file.")
        return

    try:
        pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(pdf_path).pages)
    except Exception as error:
        print(f"Gagal membaca PDF: {error}")
        return

    conversation = extract_timeline(pdf_text)
    if not conversation:
        print("Tidak ditemukan percakapan dengan format timestamp [MM:SS] di PDF.")
        return

    output_dir = os.path.join("Hasil_Notulensi", "conversation analysis results")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = os.path.join(output_dir, f"Conversation_Analysis_{timestamp}")

    txt_path = base_path + "_conversation.txt"
    with open(txt_path, "w", encoding="utf-8") as file:
        file.write(conversation)

    print("Percakapan bertimestamp berhasil diekstrak. Menganalisis seluruh percakapan...")
    analysis = _call_gemini([CONVERSATION_ANALYSIS_PROMPT + "\n" + conversation])

    pdf_output = base_path + ".pdf"
    word_output = base_path + ".docx"
    save_to_pdf(analysis, filename=pdf_output)
    export_to_word(analysis, filename=word_output)

    print(f"\nAnalisis selesai:\n-> {os.path.abspath(pdf_output)}\n-> {os.path.abspath(word_output)}")
    print(f"Teks percakapan:\n-> {os.path.abspath(txt_path)}")


if __name__ == "__main__":
    analyze_pdf_conversation()
