import importlib.util
import tempfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PLUGIN = load_module("transkrip_plugin", "__init__.py")


class FakeContext:
    def __init__(self):
        self.commands = {}

    def register_command(self, name, handler, **metadata):
        self.commands[name] = (handler, metadata)


def test_transkrip_command_registers_and_lists_all_options():
    ctx = FakeContext()
    PLUGIN.register(ctx)

    handler, metadata = ctx.commands["transkrip"]
    output = handler("")

    assert metadata["description"]
    assert "Mulai Rekam Meeting (Live AI)" in output
    assert "Upload File Audio (.wav/.mp3/.m4a) Manual" in output
    assert "Kompresi Suara Noise dan Generate Notulensi" in output
    assert "Analisis Lengkap Percakapan dari PDF" in output
    assert "Keluar transkrip" in output


def test_option_one_launches_recorder():
    launched = []

    output = PLUGIN.handle_transkrip("1", launch_recorder=lambda: launched.append(True))

    assert launched == [True]
    assert "CMD rekaman dibuka" in output


def test_option_two_launches_audio_uploader():
    launched = []

    output = PLUGIN.handle_transkrip("2", launch_uploader=lambda: launched.append(True))

    assert launched == [True]
    assert "window upload audio dibuka" in output.lower()


def test_option_three_launches_audio_compressor():
    launched = []

    output = PLUGIN.handle_transkrip("3", launch_compressor=lambda: launched.append(True))

    assert launched == [True]
    assert "window kompresi audio dibuka" in output.lower()


def test_option_four_launches_pdf_analysis():
    launched = []

    output = PLUGIN.handle_transkrip("4", launch_pdf_analysis=lambda: launched.append(True))

    assert launched == [True]
    assert "window analisis pdf dibuka" in output.lower()


def test_audio_status_distinguishes_sound_from_silence():
    recorder = load_module("audio_recorder_for_test", "audio_recorder.py")

    assert recorder.audio_status(recorder.np.array([0.0, 0.01])) == "⏳ Menunggu suara...    "
    assert recorder.audio_status(recorder.np.array([0.0, 0.06])) == "🔊 Suara terdeteksi...  "


def test_new_recording_path_creates_desktop_plugin_storage():
    recorder = load_module("audio_recorder_storage_test", "audio_recorder.py")

    with tempfile.TemporaryDirectory() as directory:
        desktop = Path(directory)
        output = recorder.new_recording_path(
            desktop=desktop,
            now=datetime(2026, 8, 28, 9, 30, 45),
        )

        root = desktop / "Hermes Transkrip"
        assert output == root / "Rekaman" / "Meeting_20260828_093045.wav"
        assert all(
            (root / name).is_dir()
            for name in ("Rekaman", "Hasil Tuning", "Transkrip", "Analisis Lengkap")
        )


def test_saved_recording_is_transcribed_and_analyzed_by_hermes():
    processor = load_module("hermes_processor_for_test", "hermes_processor.py")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "Hermes Transkrip"
        audio = root / "Rekaman" / "Meeting_20260828_093045.wav"
        audio.parent.mkdir(parents=True)
        audio.write_bytes(b"fake wav for dependency-injected test")

        result = processor.process_recording(
            audio,
            transcribe=lambda _: "[00:00] Halo meeting",
            run_hermes=lambda _: "KESIMPULAN: Meeting tervalidasi",
        )

        assert result["transcript"].read_text(encoding="utf-8") == "[00:00] Halo meeting"
        assert result["analysis_txt"].read_text(encoding="utf-8") == "KESIMPULAN: Meeting tervalidasi"
        assert result["analysis_pdf"].is_file()
        assert result["analysis_docx"].is_file()


def test_recorder_hands_saved_wav_to_processor():
    recorder = load_module("audio_recorder_handoff_test", "audio_recorder.py")
    received = []

    recorder.process_saved_recording("meeting.wav", processor=lambda path: received.append(Path(path)))

    assert received == [Path("meeting.wav")]


def test_processor_uses_deployed_prompts_without_custom_rewrite():
    source = (ROOT / "hermes_processor.py").read_text(encoding="utf-8")

    assert "initial_prompt=TRANSCRIBE_PROMPT" in source
    assert "return run_hermes_prompt(SUMMARIZE_PROMPT, transcript_path)" in source
    assert 'request = f"{prompt}\\n\\nFILE INPUT:' in source
    assert "Jangan mengarang nama pembicara, keputusan" not in source


def test_uploader_copies_supported_audio_then_processes_it():
    uploader = load_module("audio_uploader_for_test", "upload_audio.py")

    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        source = base / "meeting.m4a"
        source.write_bytes(b"audio")
        processed = []

        result = uploader.import_and_process(
            selected=source,
            processor=lambda path: processed.append(path) or {"transcript": "ok"},
            desktop=base / "Desktop",
            now=datetime(2026, 8, 28, 10, 11, 12),
        )

        copied = base / "Desktop" / "Hermes Transkrip" / "Rekaman" / "Upload_20260828_101112_meeting.m4a"
        assert copied.read_bytes() == b"audio"
        assert processed == [copied]
        assert result == {"transcript": "ok"}


def test_uploader_rejects_unsupported_audio_extension():
    uploader = load_module("audio_uploader_validation_test", "upload_audio.py")

    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "meeting.exe"
        source.write_bytes(b"not audio")
        try:
            uploader.import_and_process(selected=source, desktop=Path(directory) / "Desktop")
        except ValueError as error:
            assert ".wav/.mp3/.m4a" in str(error)
        else:
            raise AssertionError("format tidak didukung harus ditolak")


def test_compressor_saves_tuned_audio_then_uses_shared_processor():
    compressor = load_module("audio_compressor_for_test", "audio_compressor.py")

    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        source = base / "meeting.wav"
        source.write_bytes(b"audio")
        processed = []

        result = compressor.compress_and_process(
            selected=source,
            desktop=base / "Desktop",
            now=datetime(2026, 8, 30, 10, 11, 12),
            tuner=lambda _, output: output.write_bytes(b"tuned"),
            processor=lambda path: processed.append(path) or {"transcript": "ok"},
        )

        tuned = base / "Desktop" / "Hermes Transkrip" / "Hasil Tuning" / "Tuning_20260830_101112_meeting.mp3"
        assert tuned.read_bytes() == b"tuned"
        assert processed == [tuned]
        assert result == {"transcript": "ok"}


def test_pdf_timeline_excludes_summary_and_pdf_decoration():
    analysis = load_module("conversation_timeline_test", "conversation_analysis.py")
    text = """Laporan Notulensi Meeting Otomatis
Dibuat pada: 28/08/2026
[00:01] Pembicara 1: Mulai rapat.
[00:05] Pembicara 2: Baik.
**KESIMPULAN:**
Bagian ini tidak boleh masuk.
"""

    assert analysis.extract_timeline(text) == (
        "[00:01] Pembicara 1: Mulai rapat.\n"
        "[00:05] Pembicara 2: Baik."
    )


def test_pdf_analysis_writes_transcript_and_analysis_outputs():
    analysis = load_module("conversation_pdf_test", "conversation_analysis.py")

    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        source = base / "meeting.pdf"
        from pdf_generator import save_to_pdf
        save_to_pdf("[00:01] Pembicara 1: Mulai rapat.\n---\n**KESIMPULAN:**\nSelesai.", str(source))

        result = analysis.analyze_pdf_conversation(
            selected=source,
            analyzer=lambda path: "**RINGKASAN EKSEKUTIF:**\nRapat dimulai.",
            desktop=base / "Desktop",
            now=datetime(2026, 8, 28, 12, 13, 14),
        )

        root = base / "Desktop" / "Hermes Transkrip"
        assert result["conversation_txt"] == root / "Transkrip" / "Conversation_Analysis_20260828_121314_conversation.txt"
        assert "[00:01] Pembicara 1" in result["conversation_txt"].read_text(encoding="utf-8")
        assert result["analysis_txt"].is_file()
        assert result["analysis_pdf"].is_file()
        assert result["analysis_docx"].is_file()
