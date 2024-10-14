import pytest


@pytest.mark.asyncio
async def test_sqlite_database_record_and_retrieve(test_db):
    query = "Test query"
    driver = "test_driver"
    output = "Test output"
    token_usage = {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }

    query_id = await test_db.record_query(query, driver, output, token_usage)
    assert query_id is not None

    retrieved = await test_db.get_existing_query(query)
    assert retrieved is not None
    assert retrieved['query'] == query
    assert retrieved['driver'] == driver
    assert retrieved['output'] == output
    assert retrieved['token_usage'] == token_usage


@pytest.mark.asyncio
async def test_sqlite_database_nonexistent_query(test_db):
    retrieved = await test_db.get_existing_query("Nonexistent query")
    assert retrieved is None
