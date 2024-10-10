import pytest
from knish_llm_runner import CONFIG, LLMService

@pytest.mark.asyncio
@pytest.mark.skipif(not CONFIG.get('arm_model_path'), reason="ARM model path not found")
async def test_arm_driver(config, driver_selector):
    driver = driver_selector('arm')
    service = LLMService(config)
    service.driver = driver

    messages = [{"role": "user", "content": "Say 'Hello, World!'"}]
    completion, _ = await service.generate_completion(messages)

    assert "Hello, World!" in completion