from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from backend.api.models.document import DocumentUploadRequest, DocumentDraftRequest, DocumentResponse, DocumentEventLogResponse
from backend.api.services.document_service import DocumentService
from backend.agent.drafting_agent import DraftingAgent
from typing import List
import os
import logging

router = APIRouter(prefix="/documents", tags=["documents"])
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("documents_endpoint")

drafting_agent = DraftingAgent()

@router.post("/upload")
def upload_document(file: UploadFile = File(...), description: str = None):
    file_path = DocumentService.save_uploaded_file(file, description)
    logger.info(f"POST /documents/upload: {file.filename} saved at {file_path}")
    return {"filename": os.path.basename(file_path), "path": file_path}

@router.post("/draft")
def draft_document(request: DocumentDraftRequest):
    logger.info(f"POST /documents/draft: Drafting {request.doc_type} with context {request.context}")
    draft_result = drafting_agent.draft_document(request.doc_type, request.context)
    logger.info(f"Drafted document saved and event logged for {request.doc_type}")
    return {"message": draft_result}

@router.get("/outputs")
def list_documents() -> List[str]:
    files = DocumentService.list_documents()
    logger.info(f"GET /documents/outputs: {files}")
    return files

@router.get("/{filename}")
def get_document(filename: str):
    file_path = DocumentService.get_document(filename)
    if not file_path:
        logger.warning(f"GET /documents/{filename}: Not found")
        raise HTTPException(status_code=404, detail="Document not found")
    logger.info(f"GET /documents/{filename}: File served")
    return FileResponse(file_path, filename=filename)

@router.get("/event-log", response_model=DocumentEventLogResponse)
def get_event_log():
    events = DocumentService.get_event_log()
    logger.info(f"GET /documents/event-log: {len(events)} events returned")
    return DocumentEventLogResponse(events=events)

@router.get("/reports/{filename}")
def download_report(filename: str):
    reports_dir = os.path.join(os.getcwd(), 'reports')
    file_path = os.path.join(reports_dir, filename)
    if not os.path.exists(file_path):
        logger.warning(f"GET /documents/reports/{filename}: Not found")
        raise HTTPException(status_code=404, detail="Report not found")
    logger.info(f"GET /documents/reports/{filename}: File served")
    return FileResponse(file_path, filename=filename)