from typing import Dict
from .base_driver import BaseLLMDriver, LLMError
from .openai_driver import OpenAIDriver
from .anthropic_driver import AnthropicDriver
from .arm_driver import ARMDriver
from ..utils.logging import setup_logging

logger = setup_logging(__name__, 'driver')


class LLMDriverFactory:
    @staticmethod
    def create_driver(config: Dict) -> BaseLLMDriver:
        driver_type = config.get('llm_driver', 'openai')
        logger.info(f"Creating driver of type: {driver_type}")

        try:
            if driver_type == 'openai':
                return OpenAIDriver(api_key=config['openai_api_key'], model=config['openai_model'])
            elif driver_type == 'anthropic':
                return AnthropicDriver(api_key=config['anthropic_api_key'], model=config['anthropic_model'])
            elif driver_type == 'arm':
                return ARMDriver(
                    model_path=config['arm_model_path'],
                    n_ctx=config.get('arm_n_ctx', 2048),
                    n_threads=config.get('arm_n_threads', 4),
                    n_gpu_layers=config.get('arm_n_gpu_layers', 1)
                )
            else:
                raise ValueError(f"Unsupported LLM driver: {driver_type}")
        except Exception as e:
            logger.exception(f"Failed to create {driver_type} driver")
            raise LLMError(f"Failed to create {driver_type} driver: {str(e)}")
