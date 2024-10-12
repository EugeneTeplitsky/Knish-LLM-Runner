import pytest
from fastapi import HTTPException
from knish_llm_runner.utils.auth import verify_api_key
from knish_llm_runner.config import CONFIG

@pytest.mark.asyncio
async def test_verify_api_key_valid():
    valid_key = f"Bearer {CONFIG['api_key']}"
    result = await verify_api_key(valid_key)
    assert result == valid_key

@pytest.mark.asyncio
async def test_verify_api_key_invalid():
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key("Bearer invalid_key")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid API key"

@pytest.mark.asyncio
async def test_verify_api_key_missing_bearer():
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key("invalid_key")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid API key"

@pytest.mark.asyncio
async def test_verify_api_key_none():
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(None)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid API key"