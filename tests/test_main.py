from fastapi.testclient import TestClient
from knish_llm_runner.main import app

client = TestClient(app)


def test_app_initialization():
    assert app.title == "Knish LLM Runner: OpenAI-compatible LLM API"
    assert app.version == "1.0.0"

    # Check if the routes are included
    route_paths = [route.path for route in app.routes]
    assert "/v1/chat/completions" in route_paths
    assert "/v1/models" in route_paths
    assert "/health" in route_paths
