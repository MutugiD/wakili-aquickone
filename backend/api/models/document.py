from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class DocumentUploadRequest(BaseModel):
    filename: str
    description: Optional[str] = None

class DocumentDraftRequest(BaseModel):
    doc_type: str
    context: Dict[str, str]

class DocumentResponse(BaseModel):
    doc_id: str
    filename: str
    download_url: str
    metadata: Optional[Dict[str, str]] = None

class DocumentEventLogEntry(BaseModel):
    timestamp: str
    doc_type: str
    filename: str
    context: Optional[str] = None

class DocumentEventLogResponse(BaseModel):
    events: List[DocumentEventLogEntry]