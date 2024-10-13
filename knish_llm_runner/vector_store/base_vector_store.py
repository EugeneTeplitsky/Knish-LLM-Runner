from abc import ABC, abstractmethod
from typing import List, Dict

class Document:
    def __init__(self, id: str, content: str, metadata: Dict = None):
        self.id = id
        self.content = content
        self.metadata = metadata or {}

class BaseVectorStore(ABC):
    @abstractmethod
    async def add_documents(self, documents: List[Document]):
        pass

    @abstractmethod
    async def search(self, query: str, top_k: int) -> List[Document]:
        pass

    @abstractmethod
    async def delete_document(self, document_id: str):
        pass