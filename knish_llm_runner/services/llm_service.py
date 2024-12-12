from typing import Dict, List, Tuple, AsyncGenerator, Union
from ..drivers.driver_factory import LLMDriverFactory
from ..database.database_factory import DatabaseFactory
from ..utils.logging import setup_logging
from ..config import CONFIG
from ..utils.prompt import enhance_messages_with_context, count_tokens, calculate_token_usage
from ..vector_store.vector_store_factory import VectorStoreFactory

logger = setup_logging(__name__, 'service')


class LLMService:
    def __init__(self, config: Dict):
        self.config = config
        self.db_connector = DatabaseFactory.create_connector(self.config)
        self.vector_store = VectorStoreFactory.create_store(self.config)

    async def connect(self):
        """Initialize database connection."""
        await self.db_connector.connect()

    async def disconnect(self):
        """Close database connection."""
        await self.db_connector.disconnect()

    async def generate(
            self,
            messages: List[Dict[str, str]],
            temperature: float = None,
            max_tokens: int = None,
            stream: bool = False,
            model: str = None
    ) -> Union[Tuple[str, str, Dict[str, int]], AsyncGenerator[str, None]]:
        try:
            query = messages[-1]['content']
            logger.info(f"Generating {'streaming ' if stream else ''}completion for query: {query}")

            cached_response = await self.db_connector.get_existing_query(query)
            if cached_response and not stream:
                logger.info(f"Returning cached response for query: {query}")
                return cached_response['output'], cached_response['id'], cached_response['token_usage']

            relevant_docs = await self.vector_store.search(query, top_k=3)
            if relevant_docs not in [None, []]:
                messages = enhance_messages_with_context(messages, relevant_docs)

            logger.info(f"Enhanced messages: {messages}")

            if stream:
                return self._generate_stream(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=model
                )
            else:
                return await self._generate_completion(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=model
                )

        except Exception as e:
            logger.error(f"Error in generate: {str(e)}", exc_info=True)
            raise

    async def _generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int,
            model: str = None
    ) -> Tuple[str, str, Dict[str, int]]:

        # Parsing the model and driver from the requested model string
        driver_id, model_id = self._get_driver_and_model(model)

        # Creating the driver object
        driver = LLMDriverFactory.create_driver(self.config, driver_id)

        # Generating the completion
        completion = await driver.generate_completion(
            messages=messages,
            temperature=temperature or CONFIG['temperature'],
            max_tokens=max_tokens or CONFIG['max_tokens']
        )

        # Calculating token usage
        token_usage = calculate_token_usage(
            model=model_id,
            messages=messages,
            completion=completion
        )

        # Recording the query
        query_id = await self.db_connector.record_query(
            query=messages[-1]['content'],
            driver=model,
            output=completion,
            token_usage=token_usage
        )

        return completion, query_id, token_usage

    async def _generate_stream(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int,
            model: str = None
    ) -> AsyncGenerator[str, None]:
        # Parsing the model and driver from the requested model string
        driver_id, model_id = self._get_driver_and_model(model)

        # Creating the driver object
        driver = LLMDriverFactory.create_driver(self.config, driver_id)

        # Generating the completion stream
        async for chunk in driver.generate_stream(
                messages=messages,
                temperature=temperature or CONFIG['temperature'],
                max_tokens=max_tokens or CONFIG['max_tokens']
        ):
            yield chunk

    def _get_driver_and_model(self, model: str = None) -> Tuple[str, str]:
        if not model:
            driver, model = self.config['default_llm'].split(':', 1)
        else:
            driver, model = self.config['model'].split(':', 1)
        return driver, model