from __future__ import annotations
import datetime
import logging
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from .models import STTResponse, ChatRequest, ChatResponse, TTSRequest, Order, UpdateStatusRequest
from .stt import transcribe_file
from .tts import synthesize_speech
from .llm import chat_reply, quick_create_order
from .sheets import list_orders, append_order, update_status
from .config import settings

# -----------------------------------------------------------------------------
# App Setup
# -----------------------------------------------------------------------------
app = FastAPI(title="Yudi Avatar Backend", version="1.1.0")

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yudi-backend")

# -----------------------------------------------------------------------------
# Health Endpoint
# -----------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"ok": True, "time": datetime.datetime.utcnow().isoformat()}

# -----------------------------------------------------------------------------
# STT Endpoint
# -----------------------------------------------------------------------------
@app.post("/stt", response_model=STTResponse)
async def stt_endpoint(file: UploadFile = File(...)):
    try:
        # Pass UploadFile directly to your stt.py function
        text, lang = transcribe_file(file)
        return STTResponse(text=text, language=lang)
    except Exception as e:
        logger.exception("Error in /stt endpoint")
        raise HTTPException(status_code=500, detail=f"STT failed: {e}")

# -----------------------------------------------------------------------------
# Chat Endpoint
# -----------------------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        # Quick order creation
        oid = quick_create_order(req.text)
        if oid:
            reply_map = {
                "te-IN": f"మీ ఆర్డర్ ఐడి {oid}. ధన్యవాదాలు!",
                "ta-IN": f"உங்கள் ஆர்டர் ஐடி {oid}. நன்றி!",
                "hi-IN": f"आपका ऑर्डर आईडी {oid} है। धन्यवाद!",
                "en-US": f"Your order ID is {oid}. Thanks!",
            }
            lang = req.language or "en-US"
            return ChatResponse(reply=reply_map.get(lang, reply_map["en-US"]), language=lang)

        # Otherwise LLM reply
        reply = chat_reply(req.text, req.language)
        return ChatResponse(reply=reply, language=req.language or "en-US")
    except Exception as e:
        logger.exception("Error in /chat endpoint")
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

# -----------------------------------------------------------------------------
# TTS Endpoint
# -----------------------------------------------------------------------------
@app.post("/tts")
async def tts_endpoint(req: TTSRequest):
    try:
        audio_bytes, lang = synthesize_speech(req.text, req.language)
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg"
        )
    except Exception as e:
        logger.exception("Error in /tts endpoint")
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")

# -----------------------------------------------------------------------------
# Google Sheets: List Orders
# -----------------------------------------------------------------------------
@app.get("/sheet/orders")
async def sheet_list():
    try:
        return {"orders": list_orders()}
    except Exception as e:
        logger.exception("Error in /sheet/orders endpoint")
        raise HTTPException(status_code=500, detail=f"Failed to list orders: {e}")

# -----------------------------------------------------------------------------
# Google Sheets: Append Order
# -----------------------------------------------------------------------------
@app.post("/sheet/order")
async def sheet_add(order: Order):
    try:
        ts = order.timestamp or datetime.datetime.utcnow().isoformat()
        oid = order.order_id or f"ORD-{uuid.uuid4().hex[:8].upper()}"
        append_order(oid, order.name, order.item, order.quantity, order.status or "Pending", ts)
        return {"ok": True, "order_id": oid}
    except Exception as e:
        logger.exception("Error in /sheet/order endpoint")
        raise HTTPException(status_code=500, detail=f"Failed to append order: {e}")

# -----------------------------------------------------------------------------
# Google Sheets: Update Order
# -----------------------------------------------------------------------------
@app.patch("/sheet/order")
async def sheet_update(req: UpdateStatusRequest):
    try:
        res = update_status(req.order_id, req.status)
        return res
    except Exception as e:
        logger.exception("Error in /sheet/order update endpoint")
        raise HTTPException(status_code=500, detail=f"Failed to update order: {e}")
