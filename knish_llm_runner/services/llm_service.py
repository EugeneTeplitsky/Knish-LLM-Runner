from typing import Dict, List, Tuple
from ..drivers.driver_factory import LLMDriverFactory
from ..database.database_factory import DatabaseFactory
from ..utils.logging import setup_logging
from ..drivers.base_driver import LLMError
from ..config import CONFIG
from .queue_service import queue_service

logger = setup_logging(__name__, 'service')


class LLMService:
    def __init__(self, config: Dict):
        self.driver = LLMDriverFactory.create_driver(config)
        self.db_connector = DatabaseFactory.create_connector(config)

    async def connect(self):
        """Initialize database connection."""
        await self.db_connector.connect()

    async def disconnect(self):
        """Close database connection."""
        await self.db_connector.disconnect()

    async def generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float = None,
            max_tokens: int = None
    ) -> Tuple[str, str]:
        """
        Generate a completion using the LLM driver and store it in the database.

        :return: Tuple of (completion, query_id)
        """

        async def completion_task(task_messages: List[Dict[str, str]]):
            try:
                query = task_messages[-1]['content']
                logger.info(f"Generating completion for query: {query}")
                logger.debug(f"Temperature: {temperature}, Max tokens: {max_tokens}")

                cached_response = await self.db_connector.get_existing_query(query)
                if cached_response:
                    logger.info(f"Returning cached response for query: {query}")
                    return cached_response['output'], cached_response['id']

                completion = await self.driver.generate_completion(
                    messages=task_messages,
                    temperature=temperature or CONFIG['temperature'],
                    max_tokens=max_tokens or CONFIG['max_tokens']
                )

                logger.debug(f"Received completion from driver: {completion}")

                if not isinstance(completion, str):
                    raise LLMError(f"Unexpected response type from LLM driver: {type(completion)}")

                query_id = await self.db_connector.record_query(
                    query,
                    CONFIG['llm_driver'],
                    completion
                )

                logger.info(f"Generated and stored new completion for query: {query}")
                logger.debug(f"Generated completion: {completion}")
                logger.debug(f"Query ID: {query_id}")

                return completion, query_id

            except Exception as e:
                logger.error(f"Error in generate_completion: {str(e)}", exc_info=True)
                raise

        await queue_service.enqueue(lambda: completion_task(messages))
        return await queue_service.dequeue()
