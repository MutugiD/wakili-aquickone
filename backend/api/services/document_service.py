import os
import logging
from typing import Dict, Optional, List
from fastapi import UploadFile
from backend.utils.save_utils import save_drafted_document
from backend.api.models.document import DocumentEventLogEntry

OUTPUTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../docs/outputs'))
LOG_PATH = os.path.join(OUTPUTS_DIR, 'draft_events_log.csv')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("document_service")

class DocumentService:
    @staticmethod
    def save_uploaded_file(file: UploadFile, description: Optional[str] = None) -> str:
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        file_path = os.path.join(OUTPUTS_DIR, file.filename)
        with open(file_path, 'wb') as f:
            f.write(file.file.read())
        logger.info(f"Uploaded file saved: {file.filename} (desc: {description}) at {file_path}")
        # Optionally log the upload event
        return file_path

    @staticmethod
    def get_document(filename: str) -> Optional[str]:
        file_path = os.path.join(OUTPUTS_DIR, filename)
        exists = os.path.exists(file_path)
        logger.info(f"Get document: {filename} exists={exists}")
        return file_path if exists else None

    @staticmethod
    def list_documents() -> List[str]:
        files = [f for f in os.listdir(OUTPUTS_DIR) if os.path.isfile(os.path.join(OUTPUTS_DIR, f))]
        logger.info(f"List documents: {files}")
        return files

    @staticmethod
    def get_event_log() -> List[DocumentEventLogEntry]:
        events = []
        if not os.path.exists(LOG_PATH):
            logger.info("Event log requested but no log file found. Returning empty list.")
            return events
        import csv
        with open(LOG_PATH, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                events.append(DocumentEventLogEntry(**row))
        logger.info(f"Event log returned with {len(events)} entries.")
        return events