from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from pdf_generator import save_to_pdf
from prompts import SUMMARIZE_PROMPT, TRANSCRIBE_PROMPT
from word_generator import export_to_word


def _timestamp(seconds):
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]" if hours else f"[{minutes:02d}:{seconds:02d}]"


def transcribe_local(audio_path):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("faster-whisper belum terpasang") from exc

    print("\n⏳ Mentranskripsikan audio secara lokal...")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(
        str(audio_path),
        language="id",
        vad_filter=True,
        initial_prompt=TRANSCRIBE_PROMPT,
    )
    lines = [f"{_timestamp(segment.start)} {segment.text.strip()}" for segment in segments if segment.text.strip()]
    return "\n".join(lines) or "SISTEM: Audio tidak terdeteksi atau terlalu bising."


def run_hermes_prompt(prompt, input_path):
    input_path = Path(input_path).resolve()
    hermes = shutil.which("hermes")
    if not hermes:
        raise RuntimeError("CLI Hermes tidak ditemukan di PATH")

    request = f"{prompt}\n\nFILE INPUT:\n{input_path}"
    result = subprocess.run(
        [hermes, "-t", "file", "-z", request],
        cwd=input_path.parent,
        text=True,
        capture_output=True,
        timeout=3600,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Hermes gagal memproses file")
    if not result.stdout.strip():
        raise RuntimeError("Hermes tidak menghasilkan output")
    return result.stdout.strip()


def analyze_with_hermes(transcript_path):
    print("⏳ Menganalisis transkrip dengan provider aktif Hermes...")
    return run_hermes_prompt(SUMMARIZE_PROMPT, transcript_path)


def process_recording(audio_path, transcribe=None, run_hermes=None):
    audio_path = Path(audio_path).resolve()
    if not audio_path.is_file():
        raise FileNotFoundError(audio_path)

    root = audio_path.parent.parent
    transcript_dir = root / "Transkrip"
    analysis_dir = root / "Analisis Lengkap"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    transcript = (transcribe or transcribe_local)(audio_path)
    transcript_txt = transcript_dir / f"{audio_path.stem}.txt"
    transcript_pdf = transcript_dir / f"{audio_path.stem}.pdf"
    transcript_txt.write_text(transcript, encoding="utf-8")
    save_to_pdf(transcript, filename=str(transcript_pdf))

    analysis = (run_hermes or analyze_with_hermes)(transcript_txt)
    analysis_txt = analysis_dir / f"{audio_path.stem}_Analisis.txt"
    analysis_pdf = analysis_dir / f"{audio_path.stem}_Analisis.pdf"
    analysis_docx = analysis_dir / f"{audio_path.stem}_Analisis.docx"
    analysis_txt.write_text(analysis, encoding="utf-8")
    save_to_pdf(analysis, filename=str(analysis_pdf))
    export_to_word(analysis, filename=str(analysis_docx))

    print("✅ Pemrosesan selesai.")
    print(f"Transkrip:\n-> {transcript_txt}\n-> {transcript_pdf}")
    print(f"Analisis: {analysis_dir}")
    return {
        "transcript_txt": transcript_txt,
        "transcript_pdf": transcript_pdf,
        "analysis_txt": analysis_txt,
        "analysis_pdf": analysis_pdf,
        "analysis_docx": analysis_docx,
    }
