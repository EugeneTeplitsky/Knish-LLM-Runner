import aiosqlite
from typing import Dict, Optional
from .base_database import BaseDatabase
from ..utils.logging import setup_logging

logger = setup_logging(__name__, 'database')


class SQLiteDatabase(BaseDatabase):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    async def connect(self):
        try:
            self.conn = await aiosqlite.connect(self.db_path)
            await self._create_tables()
            logger.info(f"Connected to SQLite database at {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to SQLite database: {str(e)}")
            raise

    async def disconnect(self):
        if self.conn:
            await self.conn.close()
            logger.info("Disconnected from SQLite database")

    async def _create_tables(self):
        try:
            await self.conn.execute('''
                CREATE TABLE IF NOT EXISTS queries (
                    id TEXT PRIMARY KEY,
                    query TEXT UNIQUE,
                    driver TEXT,
                    output TEXT
                )
            ''')
            await self.conn.commit()
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise

    async def record_query(self, query: str, driver: str, output: str) -> str:
        try:
            query_id = f"{driver}:{hash(query)}"
            await self.conn.execute(
                "INSERT OR REPLACE INTO queries (id, query, driver, output) VALUES (?, ?, ?, ?)",
                (query_id, query, driver, output)
            )
            await self.conn.commit()
            logger.info(f"Recorded query with ID: {query_id}")
            return query_id
        except Exception as e:
            logger.error(f"Error recording query: {str(e)}")
            raise

    async def get_existing_query(self, query: str) -> Optional[Dict[str, str]]:
        try:
            async with self.conn.execute("SELECT * FROM queries WHERE query = ?", (query,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "query": row[1],
                        "driver": row[2],
                        "output": row[3]
                    }
            return None
        except Exception as e:
            logger.error(f"Error retrieving existing query: {str(e)}")
            raise
