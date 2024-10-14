import pytest

from knish_llm_runner.database.none_database import NoneDatabase


@pytest.mark.asyncio
async def test_none_database():
    db = NoneDatabase()
    query = "Test query"
    driver = "test_driver"
    output = "Test output"
    token_usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}

    query_id = await db.record_query(query, driver, output, token_usage)
    assert query_id == "none:0"

    result = await db.get_existing_query(query)
    assert result is None
