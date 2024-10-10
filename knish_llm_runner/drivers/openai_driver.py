from typing import List, Dict
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
