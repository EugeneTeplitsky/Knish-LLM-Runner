def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_generate_completion(test_client, monkeypatch):
    async def mock_generate_completion(*args, **kwargs):
        return "Test completion", "test_query_id"

    monkeypatch.setattr("knish_llm_runner.services.llm_service.LLMService.generate_completion", mock_generate_completion)

    response = test_client.post("/generate", json={
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 100
    })
    assert response.status_code == 200
    assert "Test completion" in response.text
    assert "test_query_id" in response.text