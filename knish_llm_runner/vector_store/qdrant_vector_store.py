from typing import List, Dict

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from .base_vector_store import BaseVectorStore, Document
from ..utils.logging import setup_logging

logger = setup_logging(__name__, 'vector_store')

class QdrantVectorStore(BaseVectorStore):
    def __init__(self, host: str, port: int, collection_name: str):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info(f"Initialized Qdrant store with collection: {collection_name}")
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception as e:
            logger.warning(f"Collection {self.collection_name} does not exist. Creating it now.")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )

    async def add_documents(self, documents: List[Dict]):
        try:
            points = [
                models.PointStruct(
                    id=doc["id"],
                    vector=doc["embedding"],
                    payload={
                        "content": doc["content"],
                        "document_id": doc["metadata"]["document_id"],
                        "chunk_index": doc["metadata"]["chunk_index"]
                    }
                )
                for doc in documents
            ]
            operation_info = self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Added {len(documents)} documents to Qdrant store. Operation ID: {operation_info.operation_id}")
        except Exception as e:
            logger.error(f"Error adding documents to Qdrant: {str(e)}", exc_info=True)
            raise

    async def search(self, query: str, top_k: int) -> List[Document]:
        vector = self.encoder.encode(query)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector.tolist(),
            limit=top_k
        )
        logger.info(f"Performed search in Qdrant store, found {len(results)} results")
        return [
            Document(
                id=result.id,
                content=result.payload["content"],
                metadata={k: v for k, v in result.payload.items() if k != "content"}
            )
            for result in results
        ]

    async def delete_document(self, document_id: str):
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(points=[document_id])
        )
        logger.info(f"Deleted document with id {document_id} from Qdrant store")