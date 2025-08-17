from __future__ import annotations
from gtts import gTTS
from io import BytesIO

def synthesize_speech(text: str, language: str | None):
    # Map BCP-47 to gTTS language codes
    lang = (language or "en-US").lower()
    if lang.startswith("te"): gtts_lang = "te"
    elif lang.startswith("ta"): gtts_lang = "ta"
    elif lang.startswith("hi"): gtts_lang = "hi"
    else: gtts_lang = "en"

    tts = gTTS(text=text, lang=gtts_lang)
    buf = BytesIO()
    tts.write_to_fp(buf)
    audio_bytes = buf.getvalue()
    return audio_bytes, language or "en-US"
