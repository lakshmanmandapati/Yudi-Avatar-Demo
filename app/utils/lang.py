# Map supported languages to TTS voices
SUPPORTED_LANGS = {
    "te-IN": {"voice": "te-IN-Standard-A"},
    "ta-IN": {"voice": "ta-IN-Standard-A"},
    "hi-IN": {"voice": "hi-IN-Standard-A"},
    "en-US": {"voice": "en-US-Standard-C"},
}

# STT alt language hints
ALT_CODES = ["te-IN", "ta-IN", "hi-IN", "en-US"]

def pick_language(user_lang: str | None) -> str:
    if not user_lang:
        return "en-US"
    low = user_lang.lower()
    if low.startswith("te"): return "te-IN"
    if low.startswith("ta"): return "ta-IN"
    if low.startswith("hi"): return "hi-IN"
    if low.startswith("en"): return "en-US"
    return "en-US"

def get_voice_for_lang(lang_code: str) -> str:
    return SUPPORTED_LANGS.get(lang_code, SUPPORTED_LANGS["en-US"])["voice"]
