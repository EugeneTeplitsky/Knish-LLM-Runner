from fastapi import APIRouter, Depends
from ..config import CONFIG
from ..utils.auth import verify_api_key
import time
import os

router = APIRouter()


def get_model_name():
    llm_driver = CONFIG['llm_driver']
    if llm_driver == 'openai':
        return CONFIG.get('openai_model', 'unknown')
    elif llm_driver == 'anthropic':
        return CONFIG.get('anthropic_model', 'unknown')
    elif llm_driver == 'ollama':
        return CONFIG.get('ollama_model', 'unknown')
    elif llm_driver == 'arm':
        arm_model_path = CONFIG.get('arm_model_path', '')
        return os.path.splitext(os.path.basename(arm_model_path))[0] if arm_model_path else 'unknown'
    else:
        return 'unknown'


@router.get("/v1/models")
async def list_models(api_key: str = Depends(verify_api_key)):
    llm_driver = CONFIG['llm_driver']
    model_name = get_model_name()
    model_id = f"{llm_driver}:{model_name}"

    return {
        "object": "list",
        "data": [
            {
                "id": model_id,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "organization-owner",
            }
        ]
    }