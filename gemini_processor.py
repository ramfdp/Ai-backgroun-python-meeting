import os
import re
import time
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from pydub import AudioSegment
from prompts import MEETING_PROMPT, TRANSCRIBE_PROMPT, SUMMARIZE_PROMPT

GEMINI_API_KEY = "AIzaSyACr9RVPsWbJF5i2iiVWiQ6TKZtX0WmSqQ"
client = genai.Client(api_key=GEMINI_API_KEY)
CHUNK_MS = 15 * 60 * 1000  


def _call_gemini(contents):
    """Call Gemini with model fallback on 503."""
    for attempt in range(3):
        try:
            model = "gemini-2.5-pro" if attempt == 0 else "gemini-3-flash"
            if attempt > 0:
                print(f"🔄 Beralih ke model fallback: {model}")
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=genai.types.GenerateContentConfig(temperature=0.0)
            )
            return response.text
        except Exception as e:
            msg = str(e)
            if "503" in msg or "UNAVAILABLE" in msg:
                wait = 10 * (attempt + 1)
                print(f"⚠️ Server penuh (Percobaan {attempt+1}/3). Menunggu {wait}s...")
                time.sleep(wait)
            else:
                return f"SISTEM GAGAL: API error: {msg}"
    return "SISTEM GAGAL: Server Google sedang gangguan (503)."


def _upload_and_wait(path):
    """Upload file and poll until ready. Returns file object or None."""
    f = client.files.upload(file=path)
    while f.state.name == "PROCESSING":
        time.sleep(3)
        f = client.files.get(name=f.name)
    return f if f.state.name != "FAILED" else None


def _offset_timestamps(text, offset_sec):
    """Shift [MM:SS] timestamps by offset_sec."""
    def _shift(m):
        total = int(m.group(1)) * 60 + int(m.group(2)) + offset_sec
        mm, ss = divmod(total, 60)
        hh, mm = divmod(mm, 60)
        return f"[{hh}:{mm:02d}:{ss:02d}]" if hh else f"[{mm:02d}:{ss:02d}]"
    return re.sub(r'\[(\d+):(\d+)\]', _shift, text)


def _transcribe_chunk(idx, offset_sec, chunk_path):
    """Transcribe one chunk, return (idx, adjusted_transcript)."""
    try:
        uploaded = _upload_and_wait(chunk_path)
        if not uploaded:
            return (idx, f"[Bagian {idx+1} gagal diproses server]")
        try:
            text = _call_gemini([TRANSCRIBE_PROMPT, uploaded])
            return (idx, _offset_timestamps(text, offset_sec))
        finally:
            client.files.delete(name=uploaded.name)
    finally:
        os.unlink(chunk_path)


def process_meeting_audio(audio_path):
    print("\nMemuat audio...")
    try:
        audio = AudioSegment.from_file(audio_path)
    except Exception as e:
        return f"SISTEM GAGAL: Gagal membaca audio: {e}"

    # ponytail: short meetings → single-pass, no chunking overhead
    if len(audio) <= CHUNK_MS:
        print("Mengunggah audio ke server Google...")
        try:
            uploaded = _upload_and_wait(audio_path)
            if not uploaded:
                return "SISTEM GAGAL: Server gagal memproses file audio."
            try:
                print("Menganalisis audio...")
                return _call_gemini([MEETING_PROMPT, uploaded])
            finally:
                client.files.delete(name=uploaded.name)
        except Exception as e:
            return f"SISTEM GAGAL: {e}"

    # --- Chunked path for long meetings ---
    chunks = []
    for i in range(0, len(audio), CHUNK_MS):
        tmp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        tmp.close()
        audio[i:i + CHUNK_MS].export(tmp.name, format='mp3', bitrate='64k')  # ponytail: low bitrate, speech only
        chunks.append((len(chunks), i // 1000, tmp.name))

    print(f"Audio dipecah menjadi {len(chunks)} bagian, memproses paralel...")

    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_transcribe_chunk, idx, off, p): idx for idx, off, p in chunks}
        for f in as_completed(futures):
            try:
                results.append(f.result())
            except Exception as e:
                results.append((futures[f], f"[Error: {e}]"))

    results.sort(key=lambda x: x[0])
    merged = "\n".join(text for _, text in results)

    # ponytail: text-only call, no audio upload needed
    print("Membuat ringkasan dari seluruh transkrip...")
    summary = _call_gemini([SUMMARIZE_PROMPT + "\n\nTRANSKRIP LENGKAP:\n" + merged])

    return merged + "\n\n---\n" + summary