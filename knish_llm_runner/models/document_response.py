from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_preview: str
    total_characters: int
    file_type: str
    upload_timestamp: str
