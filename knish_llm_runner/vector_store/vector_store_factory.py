from typing import Dict
from .base_vector_store import BaseVectorStore
from .qdrant_vector_store import QdrantVectorStore
from .none_vector_store import NoneVectorStore
from ..utils.logging import setup_logging

logger = setup_logging(__name__, logfile='vector_store')

class VectorStoreFactory:
    @staticmethod
    def create_store(config: Dict) -> BaseVectorStore:
        store_type = config.get('vector_store_type', 'qdrant').lower()
        logger.info(f"Creating vector store of type: {store_type}")

        try:
            if store_type == 'qdrant':
                return QdrantVectorStore(
                    host=config.get('qdrant_host', 'localhost'),
                    port=config.get('qdrant_port', 6333),
                    collection_name=config.get('qdrant_collection_name', 'documents')
                )
            elif store_type == 'none':
                logger.info("Using NoneVectorStore (RAG functionality disabled)")
                return NoneVectorStore()
            else:
                raise ValueError(f"Unsupported vector store type: {store_type}")
        except Exception as e:
            logger.exception(f"Failed to create {store_type} vector store")
            raise ValueError(f"Failed to create {store_type} vector store: {str(e)}")