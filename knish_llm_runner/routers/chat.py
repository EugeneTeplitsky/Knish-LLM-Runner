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

router = APIRouter()


@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
        request: ChatCompletionRequest,
        api_key: str = Depends(verify_api_key),
        llm_service: LLMService = Depends(lambda: LLMService(CONFIG))
):
    try:
        if request.stream:
            return StreamingResponse(stream_chat_completion(request, llm_service), media_type="text/event-stream")
        else:
            return await generate_chat_completion(request, llm_service)
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


async def generate_chat_completion(request: ChatCompletionRequest, llm_service: LLMService):
    messages = [msg.model_dump() for msg in request.messages]
    completion, query_id, token_usage = await llm_service.generate_completion(
        messages=messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens
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


async def stream_chat_completion(request: ChatCompletionRequest, llm_service: LLMService):
    messages = [msg.model_dump() for msg in request.messages]
    async for chunk in llm_service.generate_stream(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
    ):
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
