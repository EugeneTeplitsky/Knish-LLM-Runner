from typing import Dict, List, Tuple, AsyncGenerator, Union
from ..drivers.driver_factory import LLMDriverFactory
from ..database.database_factory import DatabaseFactory
from ..utils.logging import setup_logging
from ..config import CONFIG
from ..utils.prompt import enhance_messages_with_context, count_tokens
from ..vector_store.vector_store_factory import VectorStoreFactory

logger = setup_logging(__name__, 'service')


class LLMService:
    def __init__(self, config: Dict):
        self.driver = LLMDriverFactory.create_driver(config)
        self.db_connector = DatabaseFactory.create_connector(config)
        self.vector_store = VectorStoreFactory.create_store(config)
        self.model = config.get('llm_driver', 'ollama')

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
            stream: bool = False
    ) -> Union[Tuple[str, str, Dict[str, int]], AsyncGenerator[str, None]]:
        try:
            query = messages[-1]['content']
            logger.info(f"Generating {'streaming ' if stream else ''}completion for query: {query}")

            cached_response = await self.db_connector.get_existing_query(query)
            if cached_response and not stream:
                logger.info(f"Returning cached response for query: {query}")
                return cached_response['output'], cached_response['id'], cached_response['token_usage']

            relevant_docs = await self.vector_store.search(query, top_k=3)
            enhanced_messages = enhance_messages_with_context(messages, relevant_docs)

            if stream:
                return self._generate_stream(enhanced_messages, temperature, max_tokens)
            else:
                return await self._generate_completion(enhanced_messages, temperature, max_tokens)

        except Exception as e:
            logger.error(f"Error in generate: {str(e)}", exc_info=True)
            raise

    async def _generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> Tuple[str, str, Dict[str, int]]:
        completion = await self.driver.generate_completion(
            messages=messages,
            temperature=temperature or CONFIG['temperature'],
            max_tokens=max_tokens or CONFIG['max_tokens']
        )

        token_usage = self._calculate_token_usage(messages, completion)

        query_id = await self.db_connector.record_query(
            messages[-1]['content'],
            CONFIG['llm_driver'],
            completion,
            token_usage
        )

        return completion, query_id, token_usage

    async def _generate_stream(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> AsyncGenerator[str, None]:
        async for chunk in self.driver.generate_stream(
                messages=messages,
                temperature=temperature or CONFIG['temperature'],
                max_tokens=max_tokens or CONFIG['max_tokens']
        ):
            yield chunk

    def _calculate_token_usage(self, messages: List[Dict[str, str]], completion: str) -> Dict[str, int]:
        prompt_tokens = sum(count_tokens(msg['content'], self.model) for msg in messages)
        completion_tokens = count_tokens(completion, self.model)
        total_tokens = prompt_tokens + completion_tokens

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
