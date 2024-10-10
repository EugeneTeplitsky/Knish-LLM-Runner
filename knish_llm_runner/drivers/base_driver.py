from abc import ABC, abstractmethod
from typing import Dict, List, AsyncGenerator


class LLMError(Exception):
    """Custom exception class for LLM-related errors."""
    pass


class BaseLLMDriver(ABC):
    @abstractmethod
    async def generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> str:
        """
        Generate a completion based on the given messages.

        :param messages: List of message dictionaries
        :param temperature: The temperature setting for generation
        :param max_tokens: The maximum number of tokens to generate
        :return: The generated completion as a string
        :raises LLMError: If an error occurs during generation
        """
        pass

    @abstractmethod
    async def generate_stream(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming completion based on the given messages.

        :param messages: List of message dictionaries
        :param temperature: The temperature setting for generation
        :param max_tokens: The maximum number of tokens to generate
        :yield: Chunks of the generated completion as strings
        :raises LLMError: If an error occurs during generation
        """
        pass
