from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# For a simple solution, we just define an expected API_KEY
EXPECTED_API_KEY = os.getenv("APP_API_KEY", "guest-token-12345")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header or api_key_header != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials. Invalid or missing API Key.",
        )
    return api_key_header
