from pydantic import BaseModel


class LLMResponse(BaseModel):
    response: str
    query_id: str
