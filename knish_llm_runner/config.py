import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_config():
    return {
        'llm_driver': os.getenv('LLM_DRIVER', 'openai').lower(),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'openai_model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
        'anthropic_model': os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307'),
        'ollama_api_url': os.getenv('OLLAMA_API_URL', 'http://localhost:11434'),
        'ollama_model': os.getenv('OLLAMA_MODEL', 'llama3.2:1b'),
        'arm_model_path': os.getenv('ARM_MODEL_PATH'),
        'arm_n_ctx': int(os.getenv('ARM_N_CTX', '2048')),
        'arm_n_threads': int(os.getenv('ARM_N_THREADS', '4')),
        'arm_n_gpu_layers': int(os.getenv('ARM_N_GPU_LAYERS', '1')),
        'temperature': float(os.getenv('TEMPERATURE', '0.7')),
        'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'db_type': os.getenv('DB_TYPE', 'sqlite'),
        'db_path': os.getenv('DB_PATH', 'llm_api_runner.db'),
        'runner_host': os.getenv('RUNNER_HOST', '0.0.0.0'),
        'runner_port': int(os.getenv('RUNNER_PORT', '8008')),
    }


CONFIG = get_config()


def update_config(updates):
    CONFIG.update(updates)
