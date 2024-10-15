import os
import tempfile

import pytest

from knish_llm_runner.document_processing.document_ingestion import DocumentIngestion
from knish_llm_runner.services.llm_service import LLMService
from knish_llm_runner.models.document import Document
from knish_llm_runner.utils.prompt import enhance_messages_with_context


@pytest.mark.asyncio
async def test_llm_service_caching(config, driver_selector, test_db):
    driver = driver_selector('ollama')
    service = LLMService(config)
    service.driver = driver
    service.db_connector = test_db

    messages = [{"role": "user", "content": "Output a random 2-digit integer"}]

    # First call
    completion1, query_id1, token_usage1 = await service.generate(messages)

    # Second call with the same input
    completion2, query_id2, token_usage2 = await service.generate(messages)

    assert completion1 == completion2, "Cached completion should match original"
    assert query_id1 == query_id2, "Query IDs should match for cached results"
    assert token_usage1 == token_usage2, "Token usage should be the same for cached results"
    assert token_usage1['total_tokens'] > 0, "Total tokens should be greater than zero"
    assert token_usage1['prompt_tokens'] > 0, "Prompt tokens should be greater than zero"
    assert token_usage1['completion_tokens'] > 0, "Completion tokens should be greater than zero"


@pytest.mark.asyncio
async def test_llm_service_streaming(config):
    service = LLMService(config)

    messages = [{"role": "user", "content": "Say hello"}]

    chunks = []
    async for chunk in await service.generate(messages, stream=True):
        chunks.append(chunk)

    assert len(chunks) > 0, "Should receive multiple chunks"
    full_response = ''.join(chunks)
    assert any(word in full_response.lower() for word in
               ['hello', 'hi', 'greetings']), f"Response should contain a greeting. Got: {full_response}"


@pytest.mark.asyncio
async def test_llm_service_with_rag(config):
    service = LLMService(config)
    document_ingestion = DocumentIngestion()

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file.write("The capital of France is Paris.")
        temp_file_path = temp_file.name

    try:
        # Add a document to the vector store
        await document_ingestion.ingest_and_process(temp_file_path)

        messages = [{"role": "user", "content": "What is the capital of France?"}]
        completion, query_id, token_usage = await service.generate(messages)

        assert "Paris" in completion, f"Response should include information from the retrieved document. Got: {completion}"
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_llm_service_enhance_messages_with_context():
    messages = [{"role": "user", "content": "What is the capital of France?"}]
    relevant_docs = [
        Document(
            id="doc1",
            content="The capital of France is Paris.",
            metadata={
                "filename": "geography.txt",
                "file_type": ".txt",
                "upload_timestamp": "2024-10-14T12:00:00Z"
            }
        )
    ]

    enhanced_messages = enhance_messages_with_context(messages, relevant_docs)

    assert len(enhanced_messages) == 2, "Should have one additional message for context"
    assert enhanced_messages[0]["role"] == "system", "First message should be a system message with context"
    assert "The capital of France is Paris" in enhanced_messages[0][
        "content"], "Context should be included in the system message"
    assert enhanced_messages[1] == messages[0], "Original user message should be preserved"


@pytest.mark.asyncio
async def test_llm_service_calculate_token_usage(config):
    service = LLMService(config)
    service.model = "gpt-3.5-turbo"  # Set a model for token calculation

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    completion = "The capital of France is Paris."

    token_usage = service._calculate_token_usage(messages, completion)

    assert "prompt_tokens" in token_usage
    assert "completion_tokens" in token_usage
    assert "total_tokens" in token_usage
    assert token_usage["prompt_tokens"] > 0
    assert token_usage["completion_tokens"] > 0
    assert token_usage["total_tokens"] == token_usage["prompt_tokens"] + token_usage["completion_tokens"]
