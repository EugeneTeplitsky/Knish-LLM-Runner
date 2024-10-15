import os
from datetime import datetime, timezone

from ..models.document import Document
from ..utils.logging import setup_logging
from ..config import CONFIG
from .document_store import DocumentStore
from .text_chunker import TextChunker
from .embedding_generator import EmbeddingGenerator
from ..utils.pdf import process_pdf
from ..vector_store.vector_store_factory import VectorStoreFactory
import uuid

logger = setup_logging(__name__, 'document_processing')


class DocumentIngestion:
    def __init__(self):
        self.supported_extensions = CONFIG['document_processing']['supported_extensions']
        self.max_file_size = CONFIG['document_processing']['max_file_size']
        self.pdf_extraction_timeout = CONFIG['document_processing']['pdf_extraction_timeout']
        self.temp_file_path = CONFIG['document_processing']['temp_file_path']
        self.document_store = DocumentStore()
        self.text_chunker = TextChunker()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStoreFactory.create_store(CONFIG)

        # Ensure the temp directory exists
        os.makedirs(self.temp_file_path, exist_ok=True)

    async def ingest_and_process(self, file_path: str, document_id: str = None) -> Document:
        document = self.ingest_file(file_path, document_id)
        await self.process_and_store(document)
        return document

    def ingest_file(self, file_path: str, document_id: str = None) -> Document:
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension not in self.supported_extensions:
                raise ValueError(f"Unsupported file type: {file_extension}")

            if file_extension in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            elif file_extension == '.pdf':
                content = process_pdf(file_path)
            else:
                raise NotImplementedError(f"Processing for {file_extension} is not implemented yet.")

            upload_timestamp = datetime.now(timezone.utc).isoformat()

            document = Document(
                id=document_id or str(uuid.uuid4()),
                content=content,
                metadata={
                    "filename": os.path.basename(file_path),
                    "file_type": file_extension,
                    "upload_timestamp": upload_timestamp
                }
            )

            # Add to document store
            self.document_store.add_document(document)

            logger.info(f"Successfully ingested document: {file_path} with ID: {document.id}")
            return document
        except Exception as e:
            logger.error(f"Error ingesting document {file_path}: {str(e)}")
            raise

    async def process_and_store(self, document: Document):
        try:
            logger.debug(f"Processing document: {document.id}")

            chunks = self.text_chunker.chunk_text(document.content)
            logger.debug(f"Created {len(chunks)} chunks")

            embeddings = self.embedding_generator.generate_embeddings(chunks)
            logger.debug(f"Generated {len(embeddings)} embeddings")

            documents_to_store = [
                Document(
                    id=str(uuid.uuid4()),
                    content=chunk,
                    metadata={
                        "document_id": document.id,
                        "chunk_index": i,
                        "upload_timestamp": document.upload_timestamp,
                    },
                    embedding=embedding.tolist()  # Set embedding as a separate attribute
                )
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
            ]

            await self.vector_store.add_documents(documents_to_store)
            logger.info(f"Processed and stored document {document.id} in vector store at {document.upload_timestamp}")

        except Exception as e:
            logger.error(f"Error processing and storing document: {str(e)}", exc_info=True)
            raise
