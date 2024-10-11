from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from .models.chat_completion_request import ChatCompletionRequest
from .models.chat_completion_response import ChatCompletionResponse
from .models.chat_completion_chunk import ChatCompletionChunk
from .services.llm_service import LLMService
from .config import CONFIG
from .utils.logging import setup_logging
import json
import time

logger = setup_logging(__name__, logfile='main')
app = FastAPI(title="Knish LLM Runner: OpenAI-compatible LLM API", version="1.0.0",
              description="API for running large language models compatible with OpenAI's API")

llm_service = LLMService(CONFIG)

API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


async def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if not api_key or not api_key.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Extract the token part
    token = api_key.split(" ")[1]
    if token != CONFIG['api_key']:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        if request.stream:
            return StreamingResponse(stream_chat_completion(request), media_type="text/event-stream")
        else:
            return await generate_chat_completion(request)
    except HTTPException as he:
        raise he  # Re-raise HTTP exceptions (including 401 for invalid API key)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/v1/models")
async def list_models(api_key: str = Depends(verify_api_key)):
    current_driver = CONFIG['llm_driver']
    return {
        "object": "list",
        "data": [
            {
                "id": current_driver,
                "object": "model",
                "created": int(time.time()),  # Use current timestamp
                "owned_by": "organization-owner",
            }
        ]
    }

@app.get("/health")
async def health_check():
    """Endpoint for health checks."""
    return {"status": "ok"}

@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": str(exc.detail),
                "type": "invalid_request_error",
                "param": None,
                "code": None
            }
        }
    )


async def generate_chat_completion(request: ChatCompletionRequest):
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


async def stream_chat_completion(request: ChatCompletionRequest):
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

    # Send the final chunk
    final_chunk = ChatCompletionChunk(
        id=f"chatcmpl-{time.time()}",
        object="chat.completion.chunk",
        created=int(time.time()),
        model=request.model,
        choices=[{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    )
    yield f"data: {json.dumps(final_chunk.model_dump())}\n\n".encode('utf-8')
    yield b"data: [DONE]\n\n"