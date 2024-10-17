from fastapi import APIRouter, Depends
from ..config import CONFIG
from ..utils.auth import verify_api_key
from ..drivers.driver_factory import LLMDriverFactory
import time

router = APIRouter()


async def get_all_available_models():
    all_models = []
    drivers = ['openai', 'anthropic', 'ollama', 'arm']

    for driver in drivers:
        try:
            driver_instance = LLMDriverFactory.create_driver(CONFIG, driver)
            models = await driver_instance.get_available_models()
            all_models.extend([f"{driver}:{model}" for model in models])
        except Exception as e:
            print(f"Error fetching models for {driver}: {e}")

    return all_models


@router.get("/v1/models")
async def list_models(api_key: str = Depends(verify_api_key)):
    available_models = await get_all_available_models()

    return {
        "object": "list",
        "data": [
            {
                "id": model,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "organization-owner",
            }
            for model in available_models
        ]
    }