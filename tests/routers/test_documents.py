import io
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from knish_llm_runner.main import app
from knish_llm_runner.config import CONFIG
from knish_llm_runner.models.document import Document

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_verify_api_key():
    with patch('knish_llm_runner.utils.auth.verify_api_key', return_value="test_api_key"):
        yield


@pytest.fixture
def mock_document_ingestion():
    with patch('knish_llm_runner.routers.documents.DocumentIngestion') as mock:
        mock.return_value.ingest_and_process = MagicMock(return_value=Document(
            id="test_doc_id",
            content="Test content",
            metadata={
                "filename": "test.txt",
                "file_type": ".txt",
                "upload_timestamp": "2024-10-14T12:00:00Z"
            }
        ))
        mock.return_value.document_store.get_documents.return_value = [
            Document(
                id="doc1",
                content="Test content 1",
                metadata={
                    "filename": "test1.txt",
                    "file_type": ".txt",
                    "upload_timestamp": "2024-10-14T12:00:00Z"
                }
            ),
            Document(
                id="doc2",
                content="Test content 2",
                metadata={
                    "filename": "test2.txt",
                    "file_type": ".txt",
                    "upload_timestamp": "2024-10-14T13:00:00Z"
                }
            )
        ]
        yield mock


def test_upload_document(mock_document_ingestion):
    file_content = b"This is a test document"
    response = client.post(
        "/v1/documents",
        headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
        files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test_doc_id"
    assert data["filename"] == "test.txt"
    assert data["content_preview"] == "Test content"
    assert data["total_characters"] == len("Test content")
    assert data["file_type"] == ".txt"
    assert data["upload_timestamp"] == "2024-10-14T12:00:00Z"


def test_list_documents(mock_document_ingestion):
    response = client.get(
        "/v1/documents",
        headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["documents"]) == 2
    assert data["documents"][0]["id"] == "doc1"
    assert data["documents"][1]["id"] == "doc2"


def test_upload_document_invalid_api_key():
    response = client.post(
        "/v1/documents",
        headers={"Authorization": "Bearer invalid_token"},
        files={"file": ("test.txt", io.BytesIO(b"Test content"), "text/plain")}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key"}
