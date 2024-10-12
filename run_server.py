import argparse
import uvicorn
import os
import subprocess
import logging
from knish_llm_runner.config import CONFIG, update_config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def generate_self_signed_cert(cert_file, key_file):
    """Generate a self-signed certificate using OpenSSL"""
    if os.path.exists(cert_file) and os.path.exists(key_file):
        logger.info(f"Certificate files already exist. Using existing files.")
        return

    country = "US"
    state = "State"
    locality = "City"
    organization = "Organization"
    organizational_unit = "Org Unit"
    common_name = "localhost"
    email = "email@example.com"

    subject = f"/C={country}/ST={state}/L={locality}/O={organization}/OU={organizational_unit}/CN={common_name}/emailAddress={email}"

    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096", "-nodes", "-out", cert_file,
        "-keyout", key_file, "-days", "365", "-subj", subject
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Self-signed certificate generated successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating self-signed certificate: {e.stderr}")
        raise


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the LLM API server with custom settings.")
    parser.add_argument("--host", type=str, help="Host to run the server on")
    parser.add_argument("--port", type=int, help="Port to run the server on")
    parser.add_argument("--llm-driver", type=str, help="LLM driver to use (openai, anthropic, arm)")
    parser.add_argument("--temperature", type=float, help="Temperature for LLM generation")
    parser.add_argument("--max-tokens", type=int, help="Maximum tokens for LLM generation")
    parser.add_argument("--log-level", type=str, help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--ssl-keyfile", type=str, help="Path to SSL key file")
    parser.add_argument("--ssl-certfile", type=str, help="Path to SSL certificate file")
    parser.add_argument("--auto-ssl", action="store_true",
                        help="Automatically generate SSL certificate if not provided")
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
    if new_args.ssl_keyfile:
        updates['ssl_keyfile'] = new_args.ssl_keyfile
    if new_args.ssl_certfile:
        updates['ssl_certfile'] = new_args.ssl_certfile
    if new_args.auto_ssl:
        updates['auto_ssl'] = new_args.auto_ssl

    update_config(updates)


if __name__ == "__main__":
    args = parse_arguments()
    update_config_from_args(args)

    logger.info(f"Starting server with config:")
    logger.info(f"Host: {CONFIG['runner_host']}")
    logger.info(f"Port: {CONFIG['runner_port']}")
    logger.info(f"LLM Driver: {CONFIG['llm_driver']}")
    logger.info(f"Temperature: {CONFIG['temperature']}")
    logger.info(f"Max Tokens: {CONFIG['max_tokens']}")
    logger.info(f"Log Level: {CONFIG['log_level']}")
    logger.info(f"Auto SSL: {CONFIG.get('auto_ssl')}")

    ssl_config = {}
    if CONFIG.get('auto_ssl'):
        logger.info("Auto SSL is enabled. Generating self-signed certificate.")
        cert_file = "server.crt"
        key_file = "server.key"
        generate_self_signed_cert(cert_file, key_file)
        ssl_config['ssl_keyfile'] = key_file
        ssl_config['ssl_certfile'] = cert_file
    elif CONFIG.get('ssl_keyfile') and CONFIG.get('ssl_certfile'):
        ssl_config['ssl_keyfile'] = CONFIG['ssl_keyfile']
        ssl_config['ssl_certfile'] = CONFIG['ssl_certfile']
        logger.info(f"Using provided SSL certificates")
    else:
        logger.info("SSL is not configured and auto-SSL is not enabled.")

    if ssl_config:
        logger.info(f"SSL Enabled: True")
        logger.info(f"SSL Key File: {ssl_config['ssl_keyfile']}")
        logger.info(f"SSL Cert File: {ssl_config['ssl_certfile']}")
    else:
        logger.info("SSL Enabled: False")

    try:
        uvicorn.run(
            "knish_llm_runner.main:app",
            host=CONFIG['runner_host'],
            port=CONFIG['runner_port'],
            log_level=CONFIG['log_level'].lower(),
            reload=True,
            ssl_keyfile=ssl_config.get('ssl_keyfile'),
            ssl_certfile=ssl_config.get('ssl_certfile')
        )
    except Exception as e:
        logger.error(f"Error starting uvicorn server: {str(e)}", exc_info=True)