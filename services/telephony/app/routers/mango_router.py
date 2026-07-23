from fastapi import APIRouter, Form

from services.infrastructure.kafka.kafka_producer import produce_event

from fastapi import HTTPException
from hashlib import sha256

import os, hmac

mango_router = APIRouter(
    # prefix="/mango",
    tags=['Mango Integration']
)

def mango_validate_request(vpbx_api_key, sign, raw_json) -> str:
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
async def mango_recieve_call(vpbx_api_key: str = Form(...),
                             sign: str = Form(...),
                             raw_json: str = Form(..., alias="json")):
    validated_payload = mango_validate_request(vpbx_api_key, sign, raw_json)
    produce_event("mango.events.call", validated_payload)

@mango_router.post("/events/summary/")
async def mango_recieve_recording_summary(vpbx_api_key: str = Form(...),
                                          sign: str = Form(...),
                                          raw_json: str = Form(..., alias="json")):
    validated_payload = mango_validate_request(vpbx_api_key, sign, raw_json)
    produce_event("mango.events.summary", validated_payload)

@mango_router.post("/events/record/added/")
async def mango_recieve_recording(vpbx_api_key: str = Form(...),
                                  sign: str = Form(...),
                                  raw_json: str = Form(..., alias="json")):
    validated_payload = mango_validate_request(vpbx_api_key, sign, raw_json)

    # Запись звонка добавлена
    produce_event("mango.events.record.added", validated_payload)