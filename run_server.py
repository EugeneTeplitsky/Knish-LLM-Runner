import argparse
import uvicorn
from knish_llm_runner.config import CONFIG, update_config


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the LLM API server with custom settings.")
    parser.add_argument("--host", type=str, help="Host to run the server on")
    parser.add_argument("--port", type=int, help="Port to run the server on")
    parser.add_argument("--llm-driver", type=str, help="LLM driver to use (openai, anthropic, arm)")
    parser.add_argument("--temperature", type=float, help="Temperature for LLM generation")
    parser.add_argument("--max-tokens", type=int, help="Maximum tokens for LLM generation")
    parser.add_argument("--log-level", type=str, help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    return parser.parse_args()


def update_config_from_args(new_args):
    updates = {}
    if new_args.host:
        updates['runner_host'] = new_args.host
    if new_args.port:
        updates['runner_port'] = new_args.port
    if new_args.llm_driver:
        updates['llm_driver'] = new_args.llm_driver
    if new_args.temperature is not None:
        updates['temperature'] = new_args.temperature
    if new_args.max_tokens is not None:
        updates['max_tokens'] = new_args.max_tokens
    if new_args.log_level:
        updates['log_level'] = new_args.log_level

    update_config(updates)


if __name__ == "__main__":
    args = parse_arguments()
    update_config_from_args(args)

    print(f"Starting server with config:")
    print(f"Host: {CONFIG['runner_host']}")
    print(f"Port: {CONFIG['runner_port']}")
    print(f"LLM Driver: {CONFIG['llm_driver']}")
    print(f"Temperature: {CONFIG['temperature']}")
    print(f"Max Tokens: {CONFIG['max_tokens']}")
    print(f"Log Level: {CONFIG['log_level']}")

    uvicorn.run(
        "knish_llm_runner.main:app",
        host=CONFIG['runner_host'],
        port=CONFIG['runner_port'],
        log_level=CONFIG['log_level'].lower(),
        reload=True
    )