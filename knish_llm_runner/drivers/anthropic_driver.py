from typing import List, Dict, AsyncGenerator
import anthropic
from .base_driver import BaseLLMDriver, LLMError
from ..utils.logging import setup_logging

logger = setup_logging(__name__, logfile='driver')


def convert_messages_to_prompt(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    anthropic_messages = []
    for message in messages:
        role = message['role']
        content = message['content']

        if role == 'system':
            anthropic_messages.append({"role": "user", "content": content})
            anthropic_messages.append({"role": "assistant", "content": "Understood. How can I help you?"})
        elif role == 'user':
            anthropic_messages.append({"role": "user", "content": content})
        elif role == 'assistant':
            anthropic_messages.append({"role": "assistant", "content": content})
        else:
            logger.warning(f"Unknown message role: {role}. Skipping this message.")

    return anthropic_messages


class AnthropicDriver(BaseLLMDriver):
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        logger.info(f"Initialized Anthropic driver with model: {model}")

    async def generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> str:
        try:
            # Convert messages to Anthropic's format
            anthropic_messages = convert_messages_to_prompt(messages)

            logger.debug(f"Sending request to Anthropic API with messages: {anthropic_messages}")

            response = await self.client.messages.create(
                model=self.model,
                messages=anthropic_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            logger.debug(f"Received response from Anthropic API: {response}")

            if not response.content or len(response.content) == 0:
                raise LLMError("Anthropic API returned an empty response")

            # The content is a list of message contents, we'll take the first one
            return response.content[0].text

        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise LLMError(f"Anthropic API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Anthropic driver: {str(e)}")
            raise LLMError(f"Unexpected error in Anthropic driver: {str(e)}")

    async def generate_stream(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> AsyncGenerator[str, None]:
        try:
            anthropic_messages = convert_messages_to_prompt(messages)
            stream = await self.client.messages.create(
                model=self.model,
                messages=anthropic_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            async for chunk in stream:
                if chunk.delta.text:
                    yield chunk.delta.text
        except anthropic.APIError as e:
            logger.error(f"Anthropic API streaming error: {str(e)}")
            raise LLMError(f"Anthropic API streaming error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Anthropic driver streaming: {str(e)}")
            raise LLMError(f"Unexpected error in Anthropic driver streaming: {str(e)}")

    async def get_available_models(self) -> List[str]:
        # Anthropic doesn't have a models list endpoint, so we'll return a predefined list
        return ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"]
