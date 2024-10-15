from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from ..models.chat_completion_request import ChatCompletionRequest
from ..models.chat_completion_response import ChatCompletionResponse
from ..models.chat_completion_chunk import ChatCompletionChunk
from ..services.llm_service import LLMService
from ..config import CONFIG
from ..utils.auth import verify_api_key
import json
import time

from ..utils.logging import setup_logging

router = APIRouter()
logger = setup_logging(__name__, 'api')

@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
        request: ChatCompletionRequest,
        api_key: str = Depends(verify_api_key),
        llm_service: LLMService = Depends(lambda: LLMService(CONFIG))
):
    try:
        logger.error(f"Processing chat completion: {request.model_dump()}", exc_info=True)
        messages = [msg.model_dump() for msg in request.messages]
        if request.stream:
            return StreamingResponse(
                stream_chat_completion(request, llm_service, messages),
                media_type="text/event-stream"
            )
        else:
            return await generate_chat_completion(request, llm_service, messages)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def generate_chat_completion(
        request: ChatCompletionRequest,
        llm_service: LLMService,
        messages: List[Dict[str, str]]
):
    completion, query_id, token_usage = await llm_service.generate(
        messages=messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        stream=False
    )

    return ChatCompletionResponse(
        id=f"chatcmpl-{query_id}",
        object="chat.completion",
        created=int(time.time()),
        model=request.model,
        choices=[{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": completion
            },
            "finish_reason": "stop"
        }],
        usage=token_usage
    )


async def stream_chat_completion(
        request: ChatCompletionRequest,
        llm_service: LLMService,
        messages: List[Dict[str, str]]
):
    stream_generator = await llm_service.generate(
        messages=messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        stream=True
    )

    async for chunk in stream_generator:
        chunk_response = ChatCompletionChunk(
            id=f"chatcmpl-{time.time()}",
            object="chat.completion.chunk",
            created=int(time.time()),
            model=request.model,
            choices=[{
                "index": 0,
                "delta": {
                    "content": chunk
                },
                "finish_reason": None
            }]
        )
        yield f"data: {json.dumps(chunk_response.model_dump())}\n\n".encode('utf-8')
    yield b"data: [DONE]\n\n"
