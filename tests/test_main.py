import json
from fastapi.testclient import TestClient
from knish_llm_runner.main import app


def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_completion(test_client, monkeypatch):
    async def mock_generate_completion(*args, **kwargs):
        return "Test completion", "test_query_id"

    monkeypatch.setattr("knish_llm_runner.services.llm_service.LLMService.generate_completion",
                        mock_generate_completion)

    response = test_client.post("/generate", json={
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 100
    })
    assert response.status_code == 200
    assert "Test completion" in response.text
    assert "test_query_id" in response.text


def test_streaming_generation():
    client = TestClient(app)
    response = client.post("/generate/stream", json={
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Count from 1 to 5 slowly."}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    })

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream"), "Content-Type should be text/event-stream"

    chunks = []
    for line in response.iter_lines():
        if line:
            # No need to decode, as line is already a string
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    chunk = data.get("chunk", "")
                    chunks.append(chunk)
                    print(f"Received chunk: {chunk}")
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON from line: {line}")

    full_response = "".join(chunks)
    print(f"Full response: {full_response}")

    assert len(chunks) > 0, "Should receive at least one chunk"
    assert any(chunk.strip() for chunk in chunks), "At least one chunk should contain non-whitespace characters"

    # More lenient assertions about content
    numbers = [str(i) for i in range(1, 6)]
    assert any(any(num in chunk for num in numbers) for chunk in
               chunks), "Response should contain at least one number from 1 to 5"
    assert any(num in full_response for num in numbers), "Full response should contain at least one number from 1 to 5"
