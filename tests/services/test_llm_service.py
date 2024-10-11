import pytest
from knish_llm_runner.services.llm_service import LLMService

@pytest.mark.asyncio
async def test_llm_service_caching(config, driver_selector, test_db):
    driver = driver_selector('arm')
    service = LLMService(config)
    service.driver = driver
    service.db_connector = test_db

    messages = [{"role": "user", "content": "Output a random 2-digit integer"}]

    # First call
    completion1, query_id1, token_usage1 = await service.generate_completion(messages)

    # Second call with the same input
    completion2, query_id2, token_usage2 = await service.generate_completion(messages)

    assert completion1 == completion2, "Cached completion should match original"
    assert query_id1 == query_id2, "Query IDs should match for cached results"
    assert token_usage1 == token_usage2, "Token usage should be the same for cached results"
    assert token_usage1['total_tokens'] > 0, "Total tokens should be greater than zero"
    assert token_usage1['prompt_tokens'] > 0, "Prompt tokens should be greater than zero"
    assert token_usage1['completion_tokens'] > 0, "Completion tokens should be greater than zero"