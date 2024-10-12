from fastapi import APIRouter, Depends
from ..config import CONFIG
from ..utils.auth import verify_api_key
import time

router = APIRouter()

@router.get("/v1/models")
async def list_models(api_key: str = Depends(verify_api_key)):
    current_driver = CONFIG['llm_driver']
    return {
        "object": "list",
        "data": [
            {
                "id": current_driver,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "organization-owner",
            }
        ]
    }