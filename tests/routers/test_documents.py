import os
import pytest
import uuid
import time
from fastapi.testclient import TestClient
from knish_llm_runner.main import app
from knish_llm_runner.config import CONFIG
from knish_llm_runner.document_processing.document_ingestion import DocumentIngestion
from knish_llm_runner.document_processing.document_store import DocumentStore
from unittest.mock import patch

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_verify_api_key():
    with patch('knish_llm_runner.utils.auth.verify_api_key', return_value="test_api_key"):
        yield


@pytest.fixture
def document_ingestion():
    return DocumentIngestion()


@pytest.fixture
def document_store():
    store = DocumentStore()
    store.clear()  # Ensure we start with an empty store for each test
    return store


def get_test_file_path(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, '..', 'input_files', filename)


def test_upload_document(document_ingestion):
    file_path = get_test_file_path('constitution.pdf')

    with open(file_path, 'rb') as file:
        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
            files={"file": ("constitution.pdf", file, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"].endswith("constitution.pdf")
    assert data["file_type"] == ".pdf"
    assert "We the People" in data["content_preview"]
    assert data["total_characters"] > 0
    assert data["upload_timestamp"]


def test_list_documents(document_ingestion):
    test_files = ['constitution.pdf', 'bill_of_rights.pdf']

    for file in test_files:
        file_path = get_test_file_path(file)
        with open(file_path, 'rb') as file_object:
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
                files={"file": (file, file_object, "application/pdf")}
            )
            assert response.status_code == 200, f"Failed to upload {file}"

    response = client.get(
        "/v1/documents",
        headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert len(data["documents"]) >= len(
        test_files), f"Expected at least {len(test_files)} documents, but got {len(data['documents'])}"

    uploaded_filenames = [doc["filename"] for doc in data["documents"]]
    for file in test_files:
        assert any(filename.endswith(file) for filename in
                   uploaded_filenames), f"Uploaded file {file} not found in the list of documents"

    for doc in data["documents"]:
        assert doc["file_type"] in CONFIG['document_processing'][
            'supported_extensions'], f"Unexpected file type: {doc['file_type']}"


def test_upload_valid_file_types(document_ingestion):
    valid_files = [
        ("constitution.pdf", "application/pdf"),
        ("bill_of_rights.pdf", "application/pdf"),
        ("bill_of_rights.txt", "text/plain"),
        ("constitution.md", "text/markdown")
    ]
    for filename, mime_type in valid_files:
        file_path = get_test_file_path(filename)
        with open(file_path, "rb") as file:
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
                files={"file": (filename, file, mime_type)}
            )
        assert response.status_code == 200, f"Failed to upload {filename}. Response: {response.text}"
        data = response.json()
        assert data["filename"].endswith(filename)
        assert data["file_type"] == os.path.splitext(filename)[1]


def test_upload_invalid_file_type(document_ingestion):
    response = client.post(
        "/v1/documents",
        headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
        files={"file": ("test.json", b"{'content':'This is a test'}", "application/json")}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_large_file(document_ingestion, document_store):
    file_path = get_test_file_path('large_document.pdf')

    with open(file_path, 'rb') as file:
        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
            files={"file": ("large_document.pdf", file, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"].endswith("large_document.pdf")
    assert len(data["filename"]) > len("large_document.pdf")  # Ensure there's a UUID prefix
    assert uuid.UUID(data["filename"].split('_')[0], version=4)  # Validate UUID format
    assert data["file_type"] == ".pdf"
    assert data["total_characters"] > 30000  # Adjust this value based on your large document's actual size
    assert data["upload_timestamp"]

    uploaded_filename = data["filename"]
    uploaded_id = data["id"]
    print(f"Uploaded large document with filename: {uploaded_filename} and ID: {uploaded_id}")

    # Check the document store directly
    print(f"Total documents in store: {len(document_store)}")
    stored_docs = document_store.get_documents()
    print(f"Documents retrieved from store: {len(stored_docs)}")
    for doc in stored_docs:
        print(f"- ID: {doc.id}, Filename: {doc.filename}")

    # Retry logic for checking the document store
    max_retries = 5
    retry_delay = 1  # seconds
    for attempt in range(max_retries):
        stored_doc = document_store.get_document(uploaded_id)
        if stored_doc is not None:
            print(f"Found uploaded document in store on attempt {attempt + 1}")
            break
        else:
            print(
                f"Uploaded document not found in store on attempt {attempt + 1}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    else:
        pytest.fail(f"Uploaded document with ID {uploaded_id} not found in document store after {max_retries} attempts")

    assert stored_doc is not None, f"Uploaded document with ID {uploaded_id} not found in document store"
    assert stored_doc.id == uploaded_id
    assert stored_doc.filename == uploaded_filename

    # Verify that the large document appears in the list of documents
    max_retries = 5
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        list_response = client.get(
            "/v1/documents",
            headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
        )
        assert list_response.status_code == 200
        list_data = list_response.json()

        print(f"Attempt {attempt + 1}: Retrieved {len(list_data['documents'])} documents from API")

        if any(doc["id"] == uploaded_id for doc in list_data["documents"]):
            print(f"Found uploaded document in API response on attempt {attempt + 1}")
            break
        else:
            print(
                f"Uploaded document not found in API response on attempt {attempt + 1}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    else:
        print("All documents in API response:")
        for doc in list_data["documents"]:
            print(f"- ID: {doc['id']}, Filename: {doc['filename']}")
        pytest.fail(f"Large document with ID {uploaded_id} not found in the API response after {max_retries} attempts")

    assert any(doc["id"] == uploaded_id for doc in list_data["documents"]), \
        f"Large document with ID {uploaded_id} not found in the list of documents"
