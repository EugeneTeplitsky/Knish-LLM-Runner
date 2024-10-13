from fastapi import APIRouter, Depends
from ..config import CONFIG
from ..utils.auth import verify_api_key
from ..drivers.driver_factory import LLMDriverFactory
import time

router = APIRouter()


@router.get("/v1/models")
async def list_models(api_key: str = Depends(verify_api_key)):
    driver = LLMDriverFactory.create_driver(CONFIG)
    available_models = await driver.get_available_models()

    return {
        "object": "list",
        "data": [
            {
                "id": f"{CONFIG['llm_driver']}:{model}",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "organization-owner",
            }
            for model in available_models
        ]
    }
