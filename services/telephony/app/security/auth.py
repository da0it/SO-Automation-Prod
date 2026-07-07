import os
import hmac

from dotenv import load_dotenv

from fastapi import HTTPException
from hashlib import sha256

from pwdlib import p


load_dotenv()

def mango_parse_and_validate_event(vpbx_api_key: str, sign: str, raw_json: str) -> str:
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