import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse
from .models.llm_request import LLMRequest
from .services.llm_service import LLMService
from .config import CONFIG
from .utils.logging import setup_logging

logger = setup_logging(__name__, logfile='main')
app = FastAPI(title="LLM API Runner", version="1.0.0", description="API for running large language models")

llm_service = LLMService(CONFIG)


@asynccontextmanager
async def lifespan():
    try:
        await llm_service.connect()
        logger.info("LLM service connected successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {str(e)}")
        raise
    yield
    try:
        await llm_service.disconnect()
        logger.info("LLM service disconnected successfully")
    except Exception as e:
        logger.error(f"Error during LLM service shutdown: {str(e)}")


app.lifespan = lifespan


@app.post("/generate")
async def generate_completion(request: LLMRequest):
    try:
        completion_task = asyncio.create_task(llm_service.generate_completion(
            messages=[msg.model_dump() for msg in request.messages],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        ))

        async def event_stream():
            try:
                response, query_id = await completion_task
                yield f"data: {json.dumps({'response': response, 'query_id': query_id})}\n\n"
            except Exception as event_stream_exception:
                logger.error(f"Error in event stream: {str(event_stream_exception)}", exc_info=True)
                yield f"data: {json.dumps({'error': str(event_stream_exception)})}\n\n"
            yield "event: close\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/generate/stream")
async def generate_stream(request: LLMRequest):
    try:
        async def event_stream():
            try:
                async for chunk in llm_service.generate_stream(
                        messages=[msg.model_dump() for msg in request.messages],
                        temperature=request.temperature,
                        max_tokens=request.max_tokens
                ):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            except Exception as event_stream_exception:
                logger.error(f"Error in event stream: {str(event_stream_exception)}", exc_info=True)
                yield f"data: {json.dumps({'error': str(event_stream_exception)})}\n\n"
            yield "event: close\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    """Endpoint for health checks."""
    return {"status": "ok"}
