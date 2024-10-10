import pytest
from fastapi.testclient import TestClient

from knish_llm_runner import CONFIG
from knish_llm_runner.database.sqlite_database import SQLiteDatabase
from knish_llm_runner.drivers.driver_factory import LLMDriverFactory
from knish_llm_runner.main import app


@pytest.fixture
async def test_db():
    db = SQLiteDatabase(':memory:')
    await db.connect()
    yield db
    await db.disconnect()


@pytest.fixture
def config():
    return CONFIG


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def driver_selector():
    def _select_driver(driver_type):
        test_config = CONFIG.copy()
        test_config['llm_driver'] = driver_type
        return LLMDriverFactory.create_driver(test_config)

    return _select_driver
