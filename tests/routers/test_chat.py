import json
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from knish_llm_runner.main import app
from knish_llm_runner.config import CONFIG

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_verify_api_key():
    with patch('knish_llm_runner.utils.auth.verify_api_key', return_value="test_api_key"):
        yield

@pytest.fixture
def mock_llm_service():
    with patch('knish_llm_runner.routers.chat.LLMService') as mock:
        mock.return_value.generate_completion = AsyncMock(return_value=("Test completion", "test_query_id", {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}))
        mock.return_value.generate_stream = AsyncMock(return_value=iter(["Test ", "stream ", "response"]))
        yield mock

def test_chat_completion(mock_llm_service):
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello!"}],
            "temperature": 0.7,
            "max_tokens": 50
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["content"] == "Test completion"
    assert data["usage"] == {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}

@pytest.mark.asyncio
async def test_chat_completion_stream():
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Say 'Hello, World!'"}],
            "stream": True
        }
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    content = ''
    for line in response.iter_lines():
        if line:
            # Check if line is bytes or str and handle accordingly
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            content += line + '\n'
            if line.startswith('data: '):
                try:
                    data = json.loads(line.split('data: ')[1])
                    assert "choices" in data
                    assert len(data["choices"]) > 0
                    assert "delta" in data["choices"][0]
                except json.JSONDecodeError:
                    # This might be the "[DONE]" message, which is not JSON
                    assert line.strip() == 'data: [DONE]'

    assert 'data: ' in content
    assert ('content' in content) or ('[DONE]' in content)

def test_chat_completion_invalid_api_key():
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer invalid_token"},
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello!"}]
        }
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid API key"
    }

@pytest.mark.asyncio
async def test_chat_completion_service_error(mock_llm_service):
    mock_llm_service.return_value.generate_completion.side_effect = Exception("Service error")
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello!"}]
        }
    )
    assert response.status_code == 500
    assert "Internal server error" in response.text