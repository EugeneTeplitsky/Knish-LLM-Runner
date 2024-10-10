import pytest

@pytest.mark.asyncio
async def test_sqlite_database_record_and_retrieve(test_db):
    query = "Test query"
    driver = "test_driver"
    output = "Test output"

    query_id = await test_db.record_query(query, driver, output)
    assert query_id is not None

    retrieved = await test_db.get_existing_query(query)
    assert retrieved is not None
    assert retrieved['query'] == query
    assert retrieved['driver'] == driver
    assert retrieved['output'] == output

@pytest.mark.asyncio
async def test_sqlite_database_nonexistent_query(test_db):
    retrieved = await test_db.get_existing_query("Nonexistent query")
    assert retrieved is None