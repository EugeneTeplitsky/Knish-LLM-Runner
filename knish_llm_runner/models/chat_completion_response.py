from typing import List, Dict, Any, Optional

from pydantic import BaseModel


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    system_fingerprint: Optional[str] = None
