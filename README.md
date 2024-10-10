# Knish LLM Runner

Knish LLM Runner is a FastAPI-based service for running large language models (LLMs) with support for multiple providers.

## Features

- Support for multiple LLM providers (OpenAI, Anthropic, Ollama, ARM)
- Asynchronous request handling
- Built-in caching and queuing system
- Configurable via environment variables or command-line arguments
- Extensible architecture using factory patterns for drivers and databases

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/EugeneTeplitsky/Knish-LLM-Runner.git
cd knish-llm-runner
python -m venv venv
source venv/bin/activate # (or venv\Scripts\activate on Windows)
pip install -r requirements.txt
```

## Configuration

Configure the application using environment variables or by creating a `.env` file in the project root. Here are the available configuration options:

- `LLM_DRIVER`: The LLM driver to use (openai, anthropic, ollama, arm)
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: The OpenAI model to use (default: gpt-3.5-turbo)
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `ANTHROPIC_MODEL`: The Anthropic model to use (default: claude-3-haiku-20240307)
- `OLLAMA_API_URL`: URL for the Ollama API (default: http://localhost:11434)
- `OLLAMA_MODEL`: The Ollama model to use (default: llama3.2:1b)
- `ARM_MODEL_PATH`: Path to the ARM model
- `TEMPERATURE`: Temperature for LLM generation (default: 0.7)
- `MAX_TOKENS`: Maximum tokens for LLM generation (default: 1000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DB_TYPE`: Database type (default: sqlite)
- `DB_PATH`: Database path (default: llm_api_runner.db)
- `RUNNER_HOST`: Host to run the server on (default: 0.0.0.0)
- `RUNNER_PORT`: Port to run the server on (default: 8008)

## Running the Server

Start the server using the provided run script:

```bash
python run_server.py
```

You can also provide command-line arguments to override the configuration:

```bash
python run_server.py --host 127.0.0.1 --port 8000 --llm-driver openai --temperature 0.8 --max-tokens 2000 --log-level DEBUG
```

## API Usage

### Generate Completion

Send a POST request to `/generate` with the following JSON body:

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "temperature": 0.7,
  "max_tokens": 100
}
```

The response will be a streaming response with the following format:

```json
{
  "full_response": "Hello! As an AI language model, I don't have feelings, but I'm functioning well and ready to assist you. How can I help you today?",
  "json_response": null,
  "query_id": "openai:1234567890"
}
```

### Health Check

Send a GET request to `/health` to check the server status.

## Testing

Run the test suite using pytest:

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
