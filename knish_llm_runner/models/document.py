from pydantic import BaseModel
from typing import Dict, Any, Optional, List


class Document(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None

    @property
    def filename(self) -> str:
        return self.metadata.get('filename', '')

    @property
    def content_preview(self) -> str:
        return self.content[:500] + "..." if len(self.content) > 500 else self.content

    @property
    def total_characters(self) -> int:
        return len(self.content)

    @property
    def file_type(self) -> str:
        return self.metadata.get('file_type', '')

    @property
    def upload_timestamp(self) -> str:
        return self.metadata.get('upload_timestamp', '')
