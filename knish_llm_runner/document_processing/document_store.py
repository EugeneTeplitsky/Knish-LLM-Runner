import json
import os
from typing import List, Dict
from ..utils.logging import setup_logging
from ..config import CONFIG

logger = setup_logging(__name__, 'document_processing')

class DocumentStore:
    def __init__(self):
        self.store_path = CONFIG['document_processing'].get('document_store_path', 'document_store.json')
        self.documents = self._load_documents()

    def _load_documents(self) -> List[Dict]:
        if os.path.exists(self.store_path):
            with open(self.store_path, 'r') as f:
                return json.load(f)
        return []

    def _save_documents(self):
        with open(self.store_path, 'w') as f:
            json.dump(self.documents, f)

    def add_document(self, document: Dict):
        self.documents.append(document)
        self._save_documents()
        logger.info(f"Added document to store: {document['id']}")

    def get_documents(self) -> List[Dict]:
        return self.documents

    def get_document(self, doc_id: str) -> Dict:
        for doc in self.documents:
            if doc['id'] == doc_id:
                return doc
        return None

    def remove_document(self, doc_id: str):
        self.documents = [doc for doc in self.documents if doc['id'] != doc_id]
        self._save_documents()
        logger.info(f"Removed document from store: {doc_id}")