# Yudi Avatar Backend

End-to-end backend for multilingual voice ordering:
- **STT**: Local Whisper (no cloud billing)
- **LLM**: OpenAI (GPT-4o-mini)
- **Sheets**: Google Sheets API (service account; no billing)
- **TTS**: gTTS (free)

## Requirements
- Python 3.10+
- `ffmpeg` installed and available in PATH (required by Whisper & gTTS)
  - macOS (brew): `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y ffmpeg`
  - Windows: install ffmpeg and add to PATH

## Setup
1) Create a Google Cloud **Service Account** and enable **Google Sheets API** only.
   - Share your Google Sheet with the service account email (Editor).
2) Copy `.env.example` → `.env` and fill:
   - `OPENAI_API_KEY`
   - `GOOGLE_SHEETS_SPREADSHEET_ID`
   - either `GOOGLE_APPLICATION_CREDENTIALS_JSON` or `GOOGLE_APPLICATION_CREDENTIALS`
3) Install and run:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints
- `GET /health`
- `POST /stt`  (multipart audio `file`, supports webm/ogg/wav) → `{ text, language }`
- `POST /chat` (`{ text, language? }`) → `{ reply, language }`
- `POST /tts`  (`{ text, language }`) → MP3 audio
- `GET /sheet/orders`
- `POST /sheet/order`
- `PATCH /sheet/order`

## Notes
- Whisper model can be configured using `WHISPER_MODEL` env (default: `base`).
- gTTS uses Google Translate voices (unofficial). For offline TTS, switch later to Coqui TTS.
