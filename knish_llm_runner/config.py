import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_config():
    return {
        # Runner settings
        'api_key': os.getenv('API_KEY'),
        'runner_host': os.getenv('RUNNER_HOST', '0.0.0.0'),
        'runner_port': int(os.getenv('RUNNER_PORT', '8008')),

        # SSL settings
        'ssl_keyfile': os.getenv('SSL_KEYFILE'),
        'ssl_certfile': os.getenv('SSL_CERTFILE'),
        'auto_ssl': os.getenv('AUTO_SSL', 'false').lower() == "true",

        # Logging level
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),

        # LLM driver to use
        'llm_driver': os.getenv('LLM_DRIVER', 'openai').lower(),

        # OpenAI API key and model
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'openai_model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),

        # Anthropic API key and model
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
        'anthropic_model': os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307'),

        # Ollama API URL and model
        'ollama_api_url': os.getenv('OLLAMA_API_URL', 'http://localhost:11434'),
        'ollama_model': os.getenv('OLLAMA_MODEL', 'llama3.2:1b'),

        # ARM model path and parameters
        'arm_model_path': os.getenv('ARM_MODEL_PATH'),
        'arm_n_ctx': int(os.getenv('ARM_N_CTX', '2048')),
        'arm_n_threads': int(os.getenv('ARM_N_THREADS', '4')),
        'arm_n_gpu_layers': int(os.getenv('ARM_N_GPU_LAYERS', '1')),

        # Default generation parameters
        'temperature': float(os.getenv('TEMPERATURE', '0.7')),
        'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),

        # Vector store to use
        'vector_store_type': os.getenv('VECTOR_STORE_TYPE', 'qdrant'),

        # Qdrant settings
        'qdrant_host': os.getenv('QDRANT_HOST', 'localhost'),
        'qdrant_port': int(os.getenv('QDRANT_PORT', '6333')),
        'qdrant_collection_name': os.getenv('QDRANT_COLLECTION_NAME', 'documents'),

        # Database settings
        'db_type': os.getenv('DB_TYPE', 'sqlite'),
        'db_path': os.getenv('DB_PATH', 'llm_api_runner.db'),

        # Document processing settings
        'document_processing': {
            'max_file_size': 10 * 1024 * 1024,  # 10 MB
            'supported_extensions': ['.txt', '.md', '.pdf'],
            'pdf_extraction_timeout': 300,  # 5 minutes
            'temp_file_path': 'temp/',  # Temporary file storage path
            'embedding_model': 'all-MiniLM-L6-v2',  # Sentence transformer model
        }
    }


CONFIG = get_config()


def update_config(updates):
    CONFIG.update(updates)
