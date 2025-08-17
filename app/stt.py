from __future__ import annotations
from fastapi import UploadFile
import tempfile, os
import whisper

# Load model once at import time (base size for speed/accuracy tradeoff)
# You can change to 'small' if you have GPU or need better accuracy.
_MODEL = whisper.load_model(os.environ.get("WHISPER_MODEL", "base"))

# Map to BCP-47 where possible (Whisper auto-detects language)
def transcribe_file(file: UploadFile):
    # Save the uploaded audio to a temp file because whisper takes a path/bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
        audio_bytes = file.file.read()
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        # fp16 False ensures CPU compatibility
        result = _MODEL.transcribe(tmp_path, fp16=False)
        text = (result.get("text") or "").strip()
        # Whisper returns ISO 639-1 code; map to our expected codes
        lang_short = (result.get("language") or "en").lower()
        lang_map = {"te": "te-IN", "ta": "ta-IN", "hi": "hi-IN", "en": "en-US"}
        language = lang_map.get(lang_short, "en-US")
        return text, language
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
