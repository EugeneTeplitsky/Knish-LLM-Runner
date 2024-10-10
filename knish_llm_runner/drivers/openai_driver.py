from typing import List, Dict, AsyncGenerator
from openai import AsyncOpenAI
from .base_driver import BaseLLMDriver, LLMError
from ..utils.logging import setup_logging

logger = setup_logging(__name__, logfile='driver')


class OpenAIDriver(BaseLLMDriver):
    def __init__(self, api_key: str, model: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAI driver with model: {model}")

    async def generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in OpenAI driver: {str(e)}")
            raise LLMError(f"OpenAI API error: {str(e)}")

    async def generate_stream(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error in OpenAI driver streaming: {str(e)}")
            raise LLMError(f"OpenAI API streaming error: {str(e)}")
