from typing import Dict
from .base_driver import BaseLLMDriver, LLMError
from .ollama_driver import OllamaDriver
from .openai_driver import OpenAIDriver
from .anthropic_driver import AnthropicDriver
from .arm_driver import ARMDriver
from ..utils.logging import setup_logging

logger = setup_logging(__name__, 'driver')


class LLMDriverFactory:
    @staticmethod
    def create_driver(config: Dict, driver_type: str, model: str = None) -> BaseLLMDriver:
        logger.info(f"Creating driver of type: {driver_type}")

        try:
            if driver_type == 'openai':
                return OpenAIDriver(api_key=config['openai_api_key'], model=model or config['openai_model'])
            elif driver_type == 'anthropic':
                return AnthropicDriver(api_key=config['anthropic_api_key'], model=model or config['anthropic_model'])
            elif driver_type == 'ollama':
                return OllamaDriver(api_url=config['ollama_api_url'], model=model or config['ollama_model'])
            elif driver_type == 'arm':
                return ARMDriver(
                    model_path=config['arm_model_path'],
                    model=model or config['arm_model'],
                    n_ctx=config.get('arm_n_ctx', 2048),
                    n_threads=config.get('arm_n_threads', 4),
                    n_gpu_layers=config.get('arm_n_gpu_layers', 1)
                )
            else:
                raise ValueError(f"Unsupported LLM driver: {driver_type}")
        except Exception as e:
            logger.exception(f"Failed to create {driver_type} driver")
            raise LLMError(f"Failed to create {driver_type} driver: {str(e)}")
