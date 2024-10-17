from typing import List, Dict
import tiktoken

from knish_llm_runner.models.document import Document


def count_tokens(text: str, model: str) -> int:
    try:
        encoder = tiktoken.encoding_for_model(model)
        return len(encoder.encode(text))
    except KeyError:
        # Model not found. Using cl100k_base encoding.
        encoder = tiktoken.get_encoding("cl100k_base")
        return len(encoder.encode(text))

def calculate_token_usage(model: str, messages: List[Dict[str, str]], completion: str) -> Dict[str, int]:
    prompt_tokens = sum(count_tokens(msg['content'], model) for msg in messages)
    completion_tokens = count_tokens(completion, model)
    total_tokens = prompt_tokens + completion_tokens

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens
    }


def enhance_messages_with_context(messages: List[Dict[str, str]], relevant_docs: List[Document]) -> List[
    Dict[str, str]]:
    context = "\n\n".join([f"Document {i + 1}:\n{doc.content}" for i, doc in enumerate(relevant_docs)])
    system_message = {
        "role": "system",
        "content": f"You have access to the following relevant information:\n\n{context}\n\nUse this information to inform your responses when appropriate."
    }
    return [system_message] + messages
