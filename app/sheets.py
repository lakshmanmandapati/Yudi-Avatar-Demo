from __future__ import annotations
from google.oauth2 import service_account
from googleapiclient.discovery import build
from .config import settings
from typing import List, Dict, Any, Optional
import os, datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def _get_credentials():
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        raise RuntimeError("Google credentials not found. Ensure GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS_JSON is set.")
    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    return creds

def _service():
    creds = _get_credentials()
    return build("sheets", "v4", credentials=creds)

def list_orders() -> List[Dict[str, Any]]:
    service = _service()
    res = service.spreadsheets().values().get(
        spreadsheetId=settings.GOOGLE_SHEETS_SPREADSHEET_ID,
        range=settings.GOOGLE_SHEETS_RANGE
    ).execute()
    values = res.get("values", [])
    orders: List[Dict[str, Any]] = []
    for row in values[1:] if values else []:  # skip header if present
        row = row + [""] * (7 - len(row))  # ensure at least 7 columns
        orders.append({
            "order_id": row[0],
            "name": row[1],
            "item": row[2],
            "quantity": int(row[3]) if row[3] else 0,
            "status": row[4],
            "created_at": row[5],
            "updated_at": row[6],
        })
    return orders

def append_order(order_id: str, name: str, item: str, quantity: int, status: str = "Pending"):
    service = _service()
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    values = [[order_id, name, item, str(quantity), status, now, now]]  # CreatedAt + UpdatedAt
    body = {"values": values}
    service.spreadsheets().values().append(
        spreadsheetId=settings.GOOGLE_SHEETS_SPREADSHEET_ID,
        range=settings.GOOGLE_SHEETS_RANGE.split("!")[0] + "!A:G",
        valueInputOption="RAW",
        body=body
    ).execute()
    return {"ok": True, "created_at": now, "updated_at": now}

def update_status(order_id: str, status: str):
    service = _service()
    rng = settings.GOOGLE_SHEETS_RANGE
    data = service.spreadsheets().values().get(
        spreadsheetId=settings.GOOGLE_SHEETS_SPREADSHEET_ID,
        range=rng
    ).execute()
    values = data.get("values", [])
    if not values:
        raise ValueError("Sheet is empty")

    header = values[0]
    try:
        id_idx = header.index("OrderID")
        status_idx = header.index("Status")
        updated_idx = header.index("UpdatedAt")
    except ValueError:
        # fallback if headers don’t match expected names
        id_idx, status_idx, updated_idx = 0, 4, 6

    target_row_index = None
    for i, row in enumerate(values[1:], start=2):  # 1-based row index
        if len(row) > id_idx and row[id_idx] == order_id:
            target_row_index = i
            break
    if not target_row_index:
        raise ValueError(f"Order {order_id} not found")

    # new timestamp for UpdatedAt
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    sheet_name = rng.split("!")[0]

    # update both Status + UpdatedAt
    updates = [
        {
            "range": f"{sheet_name}!{chr(ord('A')+status_idx)}{target_row_index}",
            "values": [[status]],
        },
        {
            "range": f"{sheet_name}!{chr(ord('A')+updated_idx)}{target_row_index}",
            "values": [[now]],
        }
    ]

    body = {"valueInputOption": "RAW", "data": updates}
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=settings.GOOGLE_SHEETS_SPREADSHEET_ID,
        body=body
    ).execute()

    return {"ok": True, "row": target_row_index, "updated_at": now}
