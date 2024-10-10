from typing import Dict, Optional
from .base_database import BaseDatabase
from ..utils.logging import setup_logging

logger = setup_logging(__name__, 'database')


class NoneDatabase(BaseDatabase):
    async def connect(self):
        logger.info("NoneDatabase connected (no-op)")

    async def disconnect(self):
        logger.info("NoneDatabase disconnected (no-op)")

    async def record_query(self, query: str, driver: str, output: str) -> str:
        logger.debug(f"NoneDatabase: Not recording query: {query[:50]}...")
        return "none:0"  # Return a dummy query ID

    async def get_existing_query(self, query: str) -> Optional[Dict[str, str]]:
        logger.debug(f"NoneDatabase: Not retrieving query: {query[:50]}...")
        return None  # Always return None to indicate no cached result
