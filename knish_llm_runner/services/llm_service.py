from typing import Dict, List, Tuple, AsyncGenerator
import tiktoken
from ..drivers.driver_factory import LLMDriverFactory
from ..database.database_factory import DatabaseFactory
from ..utils.logging import setup_logging
from ..config import CONFIG
from .queue_service import queue_service

logger = setup_logging(__name__, 'service')

def count_tokens(text: str, model: str) -> int:
    try:
        encoder = tiktoken.encoding_for_model(model)
        return len(encoder.encode(text))
    except KeyError:
        logger.warning(f"Model {model} not found. Using cl100k_base encoding.")
        encoder = tiktoken.get_encoding("cl100k_base")
        return len(encoder.encode(text))

class LLMService:
    def __init__(self, config: Dict):
        self.driver = LLMDriverFactory.create_driver(config)
        self.db_connector = DatabaseFactory.create_connector(config)
        self.model = config.get('llm_driver', 'ollama')

    async def connect(self):
        """Initialize database connection."""
        await self.db_connector.connect()

    async def disconnect(self):
        """Close database connection."""
        await self.db_connector.disconnect()

    async def generate_stream(
            self,
            messages: List[Dict[str, str]],
            temperature: float = None,
            max_tokens: int = None
    ) -> AsyncGenerator[str, None]:
        try:
            query = messages[-1]['content']
            logger.info(f"Generating streaming completion for query: {query}")
            logger.debug(f"Temperature: {temperature}, Max tokens: {max_tokens}")

            cached_response = await self.db_connector.get_existing_query(query)
            if cached_response:
                logger.info(f"Returning cached response for query: {query}")
                yield cached_response['output']
                return

            full_response = ""
            async for chunk in self.driver.generate_stream(
                    messages=messages,
                    temperature=temperature or CONFIG['temperature'],
                    max_tokens=max_tokens or CONFIG['max_tokens']
            ):
                full_response += chunk
                yield chunk

            # Calculate token usage (this is a simple estimation, you might want to use a more accurate method)
            prompt_tokens = sum(len(msg['content'].split()) for msg in messages)
            completion_tokens = len(full_response.split())
            total_tokens = prompt_tokens + completion_tokens

            token_usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }

            query_id = await self.db_connector.record_query(
                query,
                CONFIG['llm_driver'],
                full_response,
                token_usage
            )

            logger.info(f"Generated and stored new streaming completion for query: {query}")
            logger.debug(f"Generated completion: {full_response}")
            logger.debug(f"Query ID: {query_id}")

        except Exception as e:
            logger.error(f"Error in generate_stream: {str(e)}", exc_info=True)
            raise

    async def generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float = None,
            max_tokens: int = None
    ) -> Tuple[str, str, Dict[str, int]]:
        async def completion_task() -> Tuple[str, str, Dict[str, int]]:
            try:
                query = messages[-1]['content']
                logger.info(f"Generating completion for query: {query}")

                cached_response = await self.db_connector.get_existing_query(query)
                if cached_response:
                    logger.info(f"Returning cached response for query: {query}")
                    return cached_response['output'], cached_response['id'], cached_response['token_usage']

                completion = await self.driver.generate_completion(
                    messages=messages,
                    temperature=temperature or CONFIG['temperature'],
                    max_tokens=max_tokens or CONFIG['max_tokens']
                )

                # Implement proper token counting here
                prompt_tokens = sum(len(msg['content'].split()) for msg in messages)  # Simple word count
                completion_tokens = len(completion.split())
                total_tokens = prompt_tokens + completion_tokens

                token_usage = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }

                query_id = await self.db_connector.record_query(
                    query,
                    CONFIG['llm_driver'],
                    completion,
                    token_usage
                )

                return completion, query_id, token_usage

            except Exception as e:
                logger.error(f"Error in generate_completion: {str(e)}", exc_info=True)
                raise

        return await queue_service.enqueue(completion_task)
