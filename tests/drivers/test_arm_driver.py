import pytest
import logging
from knish_llm_runner import LLMService, CONFIG

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.skipif(not CONFIG.get('arm_model_path'), reason="ARM model path not found")
async def test_arm_driver(config, driver_selector):
    try:
        driver = driver_selector('arm')
        service = LLMService(config)
        service.driver = driver

        messages = [{"role": "user", "content": "Please output ONLY the words: 'Hello, World!'"}]
        completion, query_id, token_usage = await service.generate(messages)

        assert isinstance(completion, str), f"Expected string, got {type(completion)}"
        assert "hello" in completion.lower() or "world" in completion.lower(), \
            f"Expected a greeting, but got: {completion[:100]}..."
        assert isinstance(query_id, str), f"Expected string, got {type(query_id)}"
        assert isinstance(token_usage, dict), f"Expected dict, got {type(token_usage)}"
        assert all(key in token_usage for key in ['prompt_tokens', 'completion_tokens', 'total_tokens']), \
            f"Token usage dict missing expected keys. Got: {token_usage.keys()}"
    except Exception as e:
        logger.error(f"Error in test_arm_driver: {str(e)}", exc_info=True)
        raise
