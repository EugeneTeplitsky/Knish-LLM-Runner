from abc import ABC, abstractmethod
from typing import List

from knish_llm_runner.models.document import Document


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
