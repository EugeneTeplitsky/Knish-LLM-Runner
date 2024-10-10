import pytest
from knish_llm_runner import CONFIG, LLMService


@pytest.mark.asyncio
@pytest.mark.skipif(not CONFIG.get('openai_api_key'), reason="OpenAI API key not found")
async def test_openai_driver(config, driver_selector):
    driver = driver_selector('openai')
    service = LLMService(config)
    service.driver = driver

    messages = [{"role": "user", "content": "Say 'Hello, World!'"}]
    completion, _ = await service.generate_completion(messages)

    assert "Hello, World!" in completion
