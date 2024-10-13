from typing import List
from .base_vector_store import BaseVectorStore, Document
from ..utils.logging import setup_logging

logger = setup_logging(__name__, 'vector_store')

class NoneVectorStore(BaseVectorStore):
    async def add_documents(self, documents: List[Document]):
        logger.info(f"NoneVectorStore: Not adding {len(documents)} documents (no-op)")

    async def search(self, query: str, top_k: int) -> List[Document]:
        logger.info(f"NoneVectorStore: Not searching for query: {query[:50]}... (no-op)")
        return []

    async def delete_document(self, document_id: str):
        logger.info(f"NoneVectorStore: Not deleting document {document_id} (no-op)")