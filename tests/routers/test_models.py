from fastapi.testclient import TestClient
from knish_llm_runner.main import app
from knish_llm_runner.config import CONFIG
from knish_llm_runner.drivers.driver_factory import LLMDriverFactory
import pytest
from unittest.mock import patch, AsyncMock

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_verify_api_key():
    with patch('knish_llm_runner.utils.auth.verify_api_key', return_value="test_api_key"):
        yield

@pytest.mark.asyncio
@pytest.mark.parametrize("llm_driver,mock_models,expected_models", [
    ('ollama', ['llama2', 'gpt4all'], ['ollama:llama2', 'ollama:gpt4all']),
    ('openai', ['gpt-3.5-turbo', 'gpt-4'], ['openai:gpt-3.5-turbo', 'openai:gpt-4']),
    ('anthropic', ['claude-2', 'claude-instant-1'], ['anthropic:claude-2', 'anthropic:claude-instant-1']),
    ('arm', ['model'], ['arm:model']),
])
async def test_list_models(llm_driver, mock_models, expected_models):
    with patch.dict(CONFIG, {'llm_driver': llm_driver}):
        with patch.object(LLMDriverFactory, 'create_driver') as mock_create_driver:
            mock_driver = AsyncMock()
            mock_driver.get_available_models.return_value = mock_models
            mock_create_driver.return_value = mock_driver

            response = client.get(
                "/v1/models",
                headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["object"] == "list"
            assert len(data["data"]) == len(expected_models)
            for model, expected_model in zip(data["data"], expected_models):
                assert model["id"] == expected_model
                assert model["object"] == "model"
                assert isinstance(model["created"], int)
                assert model["owned_by"] == "organization-owner"

@pytest.mark.asyncio
async def test_list_models_unknown_driver():
    with patch.dict(CONFIG, {'llm_driver': 'unknown'}):
        with patch.object(LLMDriverFactory, 'create_driver') as mock_create_driver:
            mock_driver = AsyncMock()
            mock_driver.get_available_models.return_value = []
            mock_create_driver.return_value = mock_driver

            response = client.get(
                "/v1/models",
                headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 0