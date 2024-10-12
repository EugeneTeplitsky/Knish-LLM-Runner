from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Endpoint for health checks."""
    return {"status": "ok"}