import os
from typing import List, Dict, AsyncGenerator
from llama_cpp import Llama
from .base_driver import BaseLLMDriver, LLMError
from .. import CONFIG
from ..utils.logging import setup_logging

logger = setup_logging(__name__, logfile='driver')


def convert_messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    prompt = ""
    for message in messages:
        if message['role'] == 'system':
            prompt += f"Instructions: {message['content']}\n\n"
        elif message['role'] == 'user':
            prompt += f"Human: {message['content']}\n"
        elif message['role'] == 'assistant':
            prompt += f"Assistant: {message['content']}\n"
    prompt += "Assistant:"
    return prompt


class ARMDriver(BaseLLMDriver):
    def __init__(self, model_path: str, n_ctx: int = 2048, n_threads: int = 4, n_gpu_layers: int = 1):
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_gpu_layers=n_gpu_layers
            )
            logger.info(f"Initialized ARM driver with model: {model_path}")
        except Exception as e:
            logger.error(f"Failed to initialize ARM driver: {str(e)}")
            raise LLMError(f"ARM initialization error: {str(e)}")

    async def generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> str:
        try:
            prompt = convert_messages_to_prompt(messages)
            output = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["Human:", "Assistant:"]
            )
            return output['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"Error in ARM driver: {str(e)}")
            raise LLMError(f"ARM generation error: {str(e)}")

    async def generate_stream(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int
    ) -> AsyncGenerator[str, None]:
        try:
            prompt = convert_messages_to_prompt(messages)
            stream = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["Human:", "Assistant:"],
                stream=True
            )
            for output in stream:
                yield output['choices'][0]['text']
        except Exception as e:
            logger.error(f"Error in ARM driver streaming: {str(e)}")
            raise LLMError(f"ARM streaming error: {str(e)}")

    async def get_available_models(self) -> List[str]:
        if CONFIG.get('arm_model_path'):
            return [os.path.splitext(os.path.basename(CONFIG.get('arm_model_path')))[0]]
        return []
