from contextlib import asynccontextmanager
from fastapi import FastAPI
from .routers import chat, models, health, documents
from .config import CONFIG
from .services.llm_service import LLMService
from .utils.logging import setup_logging
from .vector_store.vector_store_factory import VectorStoreFactory

logger = setup_logging(__name__, logfile='main')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up the application")
    app.state.llm_service = LLMService(CONFIG)
    await app.state.llm_service.connect()
    app.state.vector_store = VectorStoreFactory.create_store(CONFIG)

    yield

    # Shutdown
    logger.info("Shutting down the application")
    await app.state.llm_service.disconnect()
    if hasattr(app.state.vector_store, 'close'):
        await app.state.vector_store.close()


app = FastAPI(
    title="Knish LLM Runner: OpenAI-compatible LLM API",
    version="1.0.0",
    description="API for running large language models compatible with OpenAI's API",
    lifespan=lifespan
)

# Include routers
app.include_router(chat.router)
app.include_router(models.router)
app.include_router(health.router)
app.include_router(documents.router)
