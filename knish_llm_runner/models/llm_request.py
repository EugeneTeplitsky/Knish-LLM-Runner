from typing import List
from pydantic import BaseModel, Field
from .message import Message


class LLMRequest(BaseModel):
    messages: List[Message]
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(1000, gt=0, le=4096)
