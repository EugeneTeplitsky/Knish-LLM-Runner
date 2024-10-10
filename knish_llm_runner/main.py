import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse
from .models.llm_request import LLMRequest
from .services.llm_service import LLMService
from .config import CONFIG
from .utils.logging import setup_logging

# Set up logging
logger = setup_logging(__name__, logfile='main')
app = FastAPI(title="LLM API Runner", version="1.0.0", description="API for running large language models")

# Initialize LLM service
llm_service = LLMService(CONFIG)

@asynccontextmanager
async def lifespan():
    # Startup
    try:
        await llm_service.connect()
        logger.info("LLM service connected successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {str(e)}")
        raise
    yield
    # Shutdown
    try:
        await llm_service.disconnect()
        logger.info("LLM service disconnected successfully")
    except Exception as e:
        logger.error(f"Error during LLM service shutdown: {str(e)}")


@app.post("/generate")
async def generate_completion(request: LLMRequest):
    try:
        # Start the LLM generation in the background
        completion_task = asyncio.create_task(llm_service.generate_completion(
            messages=[msg.model_dump() for msg in request.messages],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        ))

        # Set up a streaming response
        async def event_stream():
            try:
                response, query_id = await completion_task
                logger.debug(f"Raw response from LLM service: {response}")

                # Extract JSON from the response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]

                logger.debug(f"Extracted JSON string: {json_str}")

                try:
                    json_response = json.loads(json_str) if json_str else None
                    logger.debug(f"Parsed JSON response: {json.dumps(json_response, indent=2)}")
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON from extracted string: {json_str}")
                    json_response = None

                formatted_response = {
                    'full_response': response,
                    'json_response': json_response,
                    'query_id': query_id
                }
                logger.debug(f"Formatted response: {json.dumps(formatted_response, indent=2)}")

                yield f"data: {json.dumps(formatted_response)}\n\n"
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


@app.post("/test")
async def test_completion():
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    try:
        response, query_id = await llm_service.generate_completion(
            messages,
            temperature=0.7,
            max_tokens=100
        )
        return {"response": response, "query_id": query_id}
    except Exception as e:
        logger.error(f"Error in test completion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
