from typing import Dict
from .base_database import BaseDatabase
from .sqlite_database import SQLiteDatabase
from .none_database import NoneDatabase
from ..utils.logging import setup_logging

logger = setup_logging(__name__, logfile='database')


class DatabaseFactory:
    @staticmethod
    def create_connector(config: Dict) -> BaseDatabase:
        db_type = config.get('db_type', 'sqlite').lower()
        if db_type == 'sqlite':
            return SQLiteDatabase(config['db_path'])
        elif db_type == 'none':
            return NoneDatabase()
        else:
            logger.error(f"Unsupported database type: {db_type}")
            raise ValueError(f"Unsupported database type: {db_type}")
