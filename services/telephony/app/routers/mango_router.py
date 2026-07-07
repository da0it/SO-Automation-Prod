from fastapi import APIRouter, Form

from app.messaging.kafka_producer import produce_event
from app.security.auth import mango_parse_and_validate_event

mango_router = APIRouter(
    # prefix="/mango",
    tags=['Mango Integration']
)

@mango_router.post("/events/call/")
async def mango_recieve_call(vpbx_api_key: str = Form(...), sign: str = Form(...), raw_json: str = Form(..., alias="json")):
    validated_payload = mango_parse_and_validate_event(vpbx_api_key, sign, raw_json)
    produce_event("mango.events.call", validated_payload)
 
@mango_router.post("/events/recording/")
async def mango_recieve_recording(vpbx_api_key: str, sign: str, raw_json: str):
    validated_payload = mango_parse_and_validate_event(vpbx_api_key, sign, raw_json)
    produce_event("mango.events.recording", validated_payload)

@mango_router.post("/events/summary/")
async def mango_recieve_recording(vpbx_api_key: str, sign: str, raw_json: str):
    validated_payload = mango_parse_and_validate_event(vpbx_api_key, sign, raw_json)
    produce_event("mango.events.summary", validated_payload)

@mango_router.post("/events/record/added/")
async def mango_recieve_recording(vpbx_api_key: str, sign: str, raw_json: str):
    validated_payload = mango_parse_and_validate_event(vpbx_api_key, sign, raw_json)
    produce_event("mango.events.record.added", validated_payload)