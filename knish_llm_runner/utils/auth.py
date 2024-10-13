from fastapi import HTTPException, Depends
from fastapi.security import APIKeyHeader
from ..config import CONFIG

API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


async def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if not api_key or not api_key.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid API key")

    token = api_key.split(" ")[1]
    if token != CONFIG['api_key']:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key
