from fastapi.testclient import TestClient
from knish_llm_runner.main import app
from knish_llm_runner.config import CONFIG
import pytest
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_verify_api_key():
    with patch('knish_llm_runner.utils.auth.verify_api_key', return_value="test_api_key"):
        yield

@pytest.mark.parametrize("llm_driver,model_config,expected_model", [
    ('openai', {'openai_model': 'gpt-3.5-turbo'}, 'openai:gpt-3.5-turbo'),
    ('anthropic', {'anthropic_model': 'claude-2'}, 'anthropic:claude-2'),
    ('ollama', {'ollama_model': 'llama2'}, 'ollama:llama2'),
    ('arm', {'arm_model_path': '/path/to/model.bin'}, 'arm:model'),
])
def test_list_models(llm_driver, model_config, expected_model):
    with patch.dict(CONFIG, {'llm_driver': llm_driver, **model_config}):
        response = client.get(
            "/v1/models",
            headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == expected_model
        assert data["data"][0]["object"] == "model"
        assert isinstance(data["data"][0]["created"], int)
        assert data["data"][0]["owned_by"] == "organization-owner"

def test_list_models_unknown_driver():
    with patch.dict(CONFIG, {'llm_driver': 'unknown'}):
        response = client.get(
            "/v1/models",
            headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"][0]["id"] == "unknown:unknown"