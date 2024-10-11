from abc import ABC, abstractmethod
from typing import Dict, Optional

class BaseDatabase(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def record_query(self, query: str, driver: str, output: str, token_usage: Dict[str, int]) -> str:
        """
        Record a new query and return its ID.
        """
        pass

    @abstractmethod
    async def get_existing_query(self, query: str) -> Optional[Dict[str, str]]:
        """
        Check if a query already exists and return its details if found.
        """
        pass