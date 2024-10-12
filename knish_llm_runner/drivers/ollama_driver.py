from typing import List, Dict, AsyncGenerator
import aiohttp
import json
from .base_driver import BaseLLMDriver, LLMError
from ..utils.logging import setup_logging

logger = setup_logging(__name__, logfile='driver')


def convert_messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    prompt = ""
    for message in messages:
        if message['role'] == 'system':
            prompt += f"System: {message['content']}\n"
        elif message['role'] == 'user':
            prompt += f"Human: {message['content']}\n"
        elif message['role'] == 'assistant':
            prompt += f"Assistant: {message['content']}\n"
    prompt += "Assistant: "
    return prompt


class OllamaDriver(BaseLLMDriver):
    def __init__(self, api_url: str, model: str):
        self.api_url = api_url
        self.model = model
        logger.info(f"Initialized Ollama driver with model: {model}")

    async def generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> str:
        full_response = ""
        async for chunk in self.generate_stream(messages, temperature, max_tokens):
            full_response += chunk
        return full_response

    async def generate_stream(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> AsyncGenerator[str, None]:
        try:
            prompt = convert_messages_to_prompt(messages)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.api_url}/api/generate",
                        json={
                            "model": self.model,
                            "prompt": prompt,
                            "temperature": temperature,
                            "max_length": max_tokens,
                            "stream": True
                        }
                ) as response:
                    if response.status != 200:
                        raise LLMError(f"Ollama API error: {response.status}")

                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line)
                                if 'response' in data:
                                    yield data['response']
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse JSON from line: {line}")
        except Exception as e:
            logger.error(f"Error in Ollama driver: {str(e)}")
            raise LLMError(f"Ollama generation error: {str(e)}")

    async def get_available_models(self) -> List[str]:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.api_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model['name'] for model in data['models']]
                    else:
                        return []
            except Exception as e:
                print(f"Error fetching Ollama models: {e}")
                return []