from __future__ import annotations
from openai import OpenAI
import re, datetime
from .config import settings
from .sheets import append_order

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def chat_reply(user_text: str, language: str | None = None) -> str:
    sys_prompt = (
        "You are a friendly tiffin-centre assistant. "
        "Reply concisely and in the same language as the user (Telugu, Tamil, Hindi, or English). "
        "You can take food orders (dish, quantity, name), check order status, and update status. "
        "If details are missing, ask for them briefly."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_text},
        ],
        temperature=0.4,
    )
    return resp.choices[0].message.content.strip()

def maybe_extract_order(user_text: str):
    # naive English pattern: "order 2 idli for Lakshman"
    m = re.search(r"(?:order|book|want)\s+(\d+)\s+([a-zA-Z]+)\s+(?:for\s+)?([A-Za-z]+)", user_text, flags=re.I)
    if m:
        qty = int(m.group(1))
        item = m.group(2).title()
        name = m.group(3).title()
        return name, item, qty
    return None

def quick_create_order(user_text: str):
    parsed = maybe_extract_order(user_text)
    if not parsed:
        return None
    name, item, qty = parsed
    order_id = datetime.datetime.utcnow().strftime("OID%H%M%S")
    append_order(order_id, name, item, qty, status="Pending")
    return order_id
