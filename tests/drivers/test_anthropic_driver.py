import pytest
from knish_llm_runner import CONFIG, LLMService


@pytest.mark.asyncio
@pytest.mark.skipif(not CONFIG.get('anthropic_api_key'), reason="Anthropic API key not found")
async def test_anthropic_driver(config, driver_selector):
    driver = driver_selector('anthropic')
    service = LLMService(config)
    service.driver = driver

    messages = [{"role": "user", "content": "Say 'Hello, World!'"}]
    completion, query_id, token_usage = await service.generate(messages)

    assert isinstance(completion, str), f"Expected string, got {type(completion)}"
    assert "Hello, World!" in completion
    assert isinstance(query_id, str), f"Expected string, got {type(query_id)}"
    assert isinstance(token_usage, dict), f"Expected dict, got {type(token_usage)}"
    assert all(key in token_usage for key in ['prompt_tokens', 'completion_tokens', 'total_tokens']), \
        f"Token usage dict missing expected keys. Got: {token_usage.keys()}"
