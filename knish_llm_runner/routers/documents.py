from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from ..document_processing.document_ingestion import DocumentIngestion
from ..models.document_list_response import DocumentListResponse
from ..models.document_response import DocumentResponse
from ..utils.auth import verify_api_key
from ..utils.logging import setup_logging
from ..config import CONFIG
import os
import uuid

router = APIRouter()
logger = setup_logging(__name__, 'api')

document_ingestion = DocumentIngestion()


@router.post("/v1/documents", response_model=DocumentResponse)
async def upload_document(
        file: UploadFile = File(...),
        api_key: str = Depends(verify_api_key)
):
    try:
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_location = os.path.join(CONFIG['document_processing']['temp_file_path'], filename)

        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        document = await document_ingestion.ingest_and_process(file_location)

        os.remove(file_location)

        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            content_preview=document.content_preview,
            total_characters=document.total_characters,
            file_type=document.file_type,
            upload_timestamp=document.upload_timestamp
        )
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while processing the document")


@router.get("/v1/documents", response_model=DocumentListResponse)
async def list_documents(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        api_key: str = Depends(verify_api_key)
) -> DocumentListResponse:
    documents = document_ingestion.document_store.get_documents()
    paginated_documents = documents[skip: skip + limit]

    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                content_preview=doc.content_preview,
                total_characters=doc.total_characters,
                file_type=doc.file_type,
                upload_timestamp=doc.upload_timestamp
            ) for doc in paginated_documents
        ]
    )
