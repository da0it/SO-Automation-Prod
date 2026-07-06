import json
import os
import hmac
from hashlib import sha256
from types import SimpleNamespace
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

load_dotenv()

mango_router = APIRouter(
    prefix="/mango",
    tags=['Mango Integration']
)

def mango_parse_and_validate_event(vpbx_api_key: str, sign: str, raw_json: str) -> dict:
    expected_key = os.getenv("VPBX_API_KEY")
    salt = os.getenv("VPBX_API_SALT")

    if not expected_key or not salt:
        raise HTTPException(status_code=500, detail="Mango API credentials are not configured")

    if vpbx_api_key != expected_key:
        raise HTTPException(status_code=403, detail="Wrong API key. Rejected")
    
    expected_sign = sha256(
        f"{vpbx_api_key}{raw_json}{salt}".encode("utf-8")
    ).hexdigest()

    if not hmac.compare_digest(expected_sign, sign):
        raise HTTPException(status_code=403, detail="Wrong Sign. Rejected")
    
    return raw_json

@mango_router.post("/events/call/")
async def mango_recieve_call(vpbx_api_key: str, sign: str, raw_json: str):
    validated_payload = mango_parse_and_validate_event(vpbx_api_key, sign, raw_json)

    
    
# @mango_router.post("/events/call/recording")
# async def mango_recieve_recording(vpbx_api_key: str, sign: str, raw_json: str):
#     validated_payload = mango_parse_and_validate_event(vpbx_api_key, sign, raw_json)
#     json_payload = json.loads(validated_payload, object_hook=lambda d: SimpleNamespace(**d))

#     if json_payload.recording_state == "started":
#         create_ticket_record_d(.......)
#         return ticket
#     if payload.recording_state == "Completed"
#     update_ticket_state(.....)
#     return ticket
    