from typing import List
from pydantic import BaseModel

from knish_llm_runner.models.document_response import DocumentResponse


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
