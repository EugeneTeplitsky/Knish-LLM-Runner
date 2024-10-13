from fastapi import FastAPI
from .routers import chat, models, health, documents
from .config import CONFIG
from .services.llm_service import LLMService
from .utils.logging import setup_logging

logger = setup_logging(__name__, logfile='main')

app = FastAPI(
    title="Knish LLM Runner: OpenAI-compatible LLM API",
    version="1.0.0",
    description="API for running large language models compatible with OpenAI's API"
)

# Initialize LLM service
llm_service = LLMService(CONFIG)

# Include routers
app.include_router(chat.router)
app.include_router(models.router)
app.include_router(health.router)
app.include_router(documents.router)