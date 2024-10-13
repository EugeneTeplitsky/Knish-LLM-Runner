from fastapi import APIRouter, UploadFile, File, Depends, Query
from fastapi.responses import JSONResponse
from ..document_processing.document_ingestion import DocumentIngestion
from ..utils.auth import verify_api_key
from ..utils.logging import setup_logging
from ..config import CONFIG
import os
import uuid
from typing import List, Dict

router = APIRouter()
logger = setup_logging(__name__, 'api')

# Initialize DocumentIngestion
document_ingestion = DocumentIngestion()


@router.post("/v1/documents")
async def upload_document(
        file: UploadFile = File(...),
        api_key: str = Depends(verify_api_key)
):
    try:
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_location = os.path.join(CONFIG['document_processing']['temp_file_path'], filename)

        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        result = await document_ingestion.ingest_and_process(file_location)

        os.remove(file_location)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Document processed and stored successfully",
                "document": {
                    "id": result["id"],
                    "filename": result["filename"],
                    "content_preview": result["content_preview"],
                    "total_characters": result["total_characters"],
                    "file_type": result["file_type"]
                }
            }
        )
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An error occurred while processing the document",
                "error": str(e)
            }
        )


@router.get("/v1/documents")
async def list_documents(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        api_key: str = Depends(verify_api_key)
) -> List[Dict]:
    documents = document_ingestion.document_store.get_documents()
    return documents[skip: skip + limit]