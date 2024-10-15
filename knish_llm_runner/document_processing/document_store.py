import json
import os
from typing import List, Optional, Dict
from ..models.document import Document
from ..utils.logging import setup_logging
import threading

logger = setup_logging(__name__, 'document_processing')


class DocumentStore:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DocumentStore, cls).__new__(cls)
                    cls._instance.store_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                                            'document_store.json')
                    cls._instance.documents = cls._instance._load_documents()
        return cls._instance

    def _load_documents(self) -> Dict[str, Document]:
        try:
            if os.path.exists(self.store_path):
                with open(self.store_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return {doc['id']: Document(**doc) for doc in data}
                    elif isinstance(data, dict):
                        return {doc_id: Document(**doc_data) for doc_id, doc_data in data.items()}
                    else:
                        logger.error(f"Unexpected data format in {self.store_path}")
                        return {}
            return {}
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            return {}

    def _save_documents(self):
        try:
            with open(self.store_path, 'w') as f:
                json.dump({doc_id: doc.model_dump() for doc_id, doc in self.documents.items()}, f)
            logger.debug(f"Saved {len(self.documents)} documents to {self.store_path}")
        except Exception as e:
            logger.error(f"Error saving documents: {str(e)}")

    def add_document(self, document: Document):
        with self._lock:
            self.documents[document.id] = document
            self._save_documents()
        logger.info(f"Added document to store: {document.id}. Total documents: {len(self.documents)}")

    def get_documents(self) -> List[Document]:
        with self._lock:
            docs = list(self.documents.values())
        logger.debug(f"Retrieved {len(docs)} documents from store")
        return docs

    def get_document(self, doc_id: str) -> Optional[Document]:
        with self._lock:
            doc = self.documents.get(doc_id)
        if doc:
            logger.debug(f"Retrieved document {doc_id} from store")
        else:
            logger.debug(f"Document {doc_id} not found in store")
        return doc

    def remove_document(self, doc_id: str):
        with self._lock:
            if doc_id in self.documents:
                del self.documents[doc_id]
                self._save_documents()
                logger.info(f"Removed document from store: {doc_id}. Total documents: {len(self.documents)}")
            else:
                logger.warning(f"Attempted to remove non-existent document: {doc_id}")

    def clear(self):
        with self._lock:
            self.documents.clear()
            self._save_documents()
        logger.info("Cleared all documents from store")

    def __len__(self):
        return len(self.documents)
