import pytest
from knish_llm_runner import CONFIG, LLMService


@pytest.mark.asyncio
@pytest.mark.skipif(not CONFIG.get('anthropic_api_key'), reason="Anthropic API key not found")
async def test_anthropic_driver(config, driver_selector):
    driver = driver_selector('anthropic')
    service = LLMService(config)
    service.driver = driver

    messages = [{"role": "user", "content": "Say 'Hello, World!'"}]
    completion, _ = await service.generate_completion(messages)

    assert "Hello, World!" in completion
