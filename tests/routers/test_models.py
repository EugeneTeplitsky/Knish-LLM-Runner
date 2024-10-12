from fastapi.testclient import TestClient
from knish_llm_runner.main import app
from knish_llm_runner.config import CONFIG

client = TestClient(app)

def test_list_models():
    response = client.get(
        "/v1/models",
        headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == CONFIG['llm_driver']
    assert data["data"][0]["object"] == "model"
    assert isinstance(data["data"][0]["created"], int)
    assert data["data"][0]["owned_by"] == "organization-owner"