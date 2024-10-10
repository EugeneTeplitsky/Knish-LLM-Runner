import pytest
from knish_llm_runner import CONFIG, LLMService


@pytest.mark.asyncio
@pytest.mark.skipif(not CONFIG.get('ollama_api_url'), reason="Ollama API URL not found")
async def test_ollama_driver(config, driver_selector):
    driver = driver_selector('ollama')
    service = LLMService(config)
    service.driver = driver

    messages = [{"role": "user", "content": "Say 'Hello, World!'"}]
    completion, _ = await service.generate_completion(messages)

    assert completion.strip(), "Completion should not be empty"
    assert len(completion) > 10, "Completion should have a reasonable length"
    assert "Hello" in completion, "Completion should contain a greeting"
