from pydantic import BaseModel, Field
from typing import Optional

class STTResponse(BaseModel):
    text: str
    language: str

class ChatRequest(BaseModel):
    text: str
    session_id: Optional[str] = None
    language: Optional[str] = None  # 'te-IN','ta-IN','hi-IN','en-US'

class ChatResponse(BaseModel):
    reply: str
    language: str

class TTSRequest(BaseModel):
    text: str
    language: str

class Order(BaseModel):
    order_id: str
    name: str
    item: str
    quantity: int = Field(ge=1)
    status: str = "Pending"
    timestamp: Optional[str] = None

class UpdateStatusRequest(BaseModel):
    order_id: str
    status: str
