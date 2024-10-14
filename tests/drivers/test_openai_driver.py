import pytest
import logging
from knish_llm_runner import CONFIG, LLMService

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.skipif(not CONFIG.get('openai_api_key'), reason="OpenAI API key not found")
async def test_openai_driver(config, driver_selector):
    try:
        driver = driver_selector('openai')
        service = LLMService(config)
        service.driver = driver

        messages = [{"role": "user", "content": "Say 'Hello, World!'"}]
        completion, query_id, token_usage = await service.generate(messages)

        assert isinstance(completion, str), f"Expected string, got {type(completion)}"
        assert "hello" in completion.lower() and "world" in completion.lower(), \
            f"Expected 'Hello, World!', but got: {completion[:100]}..."
        assert isinstance(query_id, str), f"Expected string, got {type(query_id)}"
        assert isinstance(token_usage, dict), f"Expected dict, got {type(token_usage)}"
        assert all(key in token_usage for key in ['prompt_tokens', 'completion_tokens', 'total_tokens']), \
            f"Token usage dict missing expected keys. Got: {token_usage.keys()}"
    except Exception as e:
        logger.error(f"Error in test_openai_driver: {str(e)}", exc_info=True)
        raise
